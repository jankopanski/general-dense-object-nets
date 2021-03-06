import torch
import torch.nn as nn

def dispatch_sampler(config):
    name = config['name']
    if name == 'random':
        return RandomSampler()
    elif name == 'ring':
        inner_radius = config['inner_radius']
        outter_radius = config['outter_radius']
        return RingSampler(inner_radius=inner_radius, outter_radius=outter_radius)
    elif name == 'don':
        mask_weight = config['mask_weight']
        background_weight = config['background_weight']
        return DONSampler(mask_weight=mask_weight, background_weight=background_weight)
    else:
        raise Exception("Sampler: {} not recognized. Supported sampling strategies are: [random, ring, don]".format(name))


class Sampler(nn.Module):
    """
    Abstract class for sampling non-correspondence
    """
    def __init__(self, image_width=640, image_height=480):
        nn.Module.__init__(self)
        self.image_width = image_width
        self.image_height = image_height

    def get_samples(self, num_samples, dataset_item):
        raise NotImplementedError('Abstract method')

# this class is inspired by Ngh2Sampler from https://github.com/naver/r2d2/blob/master/nets/sampler.py
class RingSampler(Sampler):
    """
    Class for sampling non-correspondence.
    Points are being drawn from the ring around true match
    Radius is defined in pixel units.
    """
    def __init__(self, image_width=640, image_height=480, inner_radius=10, outter_radius=12):
        Sampler.__init__(self, image_width=640, image_height=480)
        self.inner_radius = inner_radius
        self.outter_radius = outter_radius
        self.sample_offsets()

    def sample_offsets(self, image_width=640):
        inner_r2 = self.inner_radius**2
        outer_r2 = self.outter_radius**2
        neg = []
        for j in range(-self.outter_radius-1, self.outter_radius+1):
            for i in range(-self.outter_radius-1, self.outter_radius+1):
                d2 = i*i + j*j
                if inner_r2 <= d2 <= outer_r2:
                    neg.append(i * image_width + j)

        self.register_buffer('negative_offsets', torch.LongTensor(neg))

    def get_offsets(self, num_samples):
        if num_samples < 0:
            raise Exception('Number of samples must be positive')
        num_offsets = len(self.negative_offsets)
        indices = torch.randint(0, num_offsets, (num_samples, ))
        return self.negative_offsets[indices]

    def get_samples(self, num_samples, dataset_item):
        offsets = self.get_offsets(num_samples)
        offsetted_points = dataset_item.matches_b[:,None] + offsets

        max_pixel_index = self.image_width * self.image_height - 1
        return offsetted_points.clamp(0, max_pixel_index)

class RandomSampler(Sampler):
    """
    Class for sampling non-correspondence.
    Points are being drawn randomly
    """
    def __init__(self, image_width=640, image_height=480):
        Sampler.__init__(self, image_width=640, image_height=480)

    def get_samples(self, num_samples, dataset_item):
        if num_samples < 0:
            raise Exception('Number of samples must be positive number')

        max_pixel_index = self.image_width * self.image_height
        samples = torch.randint(0, max_pixel_index, (num_samples, ))
        return samples.long()

class DONSampler(Sampler):
    """
    Class for sampling non-correspondence
    Points are being drawn from input
    """
    def __init__(self, image_width=640, image_height=480, mask_weight=1, background_weight=1):
        Sampler.__init__(self, image_width=640, image_height=480)
        self.mask_weight = mask_weight
        self.background_weight = background_weight

    def reshape_don_non_matches(self, non_matches):
        num_non_matches = len(non_matches)
        return  torch.reshape(non_matches, (-1, num_non_matches))

    def get_samples(self, num_samples, dataset_item):
        if num_samples < 0:
            raise Exception('Number of samples must be positive')

        masked = self.reshape_don_non_matches(dataset_item.masked_non_matches_b)
        masked_num_samples = int(num_samples * self.mask_weight / (self.mask_weight + self.background_weight))
        random_indices = torch.randint(0, masked.shape[1], (masked_num_samples,))
        masked_points = masked[:, random_indices]

        background = self.reshape_don_non_matches(dataset_item.background_non_matches_b)
        background_num_samples = num_samples - masked_num_samples
        random_indices = torch.randint(0, background.shape[1], (background_num_samples,))
        background_points = background[:, random_indices]

        assert num_samples == masked_num_samples + background_num_samples
        assert masked_num_samples > 0
        assert background_num_samples > 0

        return torch.cat([masked_points, background_points], dim=-1)

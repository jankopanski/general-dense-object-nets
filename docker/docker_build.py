#!/usr/bin/env python
from __future__ import print_function

import argparse
import os
import getpass

if __name__=="__main__":

	print("building docker container . . . ")
	user_name = getpass.getuser()
	default_image_name = user_name + "-pytorch-dense-correspondence"


	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--user_name", type=str, help="username inside docker image", default=user_name)
	parser.add_argument("-i", "--image", type=str,
		help="name for the newly created docker image", default=default_image_name)

	parser.add_argument("-d", "--dry_run", action='store_true', help="(optional) perform a dry_run, print the command that would have been executed but don't execute it.")

	parser.add_argument("-pw", "--password", type=str,
                        help="(optional) password for the user", default="password")

	parser.add_argument('-uid','--user_id', type=int, help="(optional) user id for this user", default=os.getuid())
	parser.add_argument('-gid','--group_id', type=int, help="(optional) user gid for this user", default=os.getgid())

	parser.add_argument('-p', "--passthrough", type=str, help="(optional) passthrough arguments to add to the docker build")

	args = parser.parse_args()
	print("building docker image named ", args.image)
	cmd = "docker build --build-arg USER_NAME=%(user_name)s \
			--build-arg USER_PASSWORD=%(password)s \
			--build-arg USER_ID=%(user_id)s \
			--build-arg USER_GID=%(group_id)s" \
			%{'user_name': args.user_name, 'password': args.password, 'user_id': args.user_id, 'group_id': args.group_id}

	if args.passthrough:
		cmd += " " + args.passthrough

	cmd += " -t %s -f pytorch-dense-correspondence.dockerfile ." % args.image
	

	print("command = \n \n", cmd)
	print("")

	# build the docker image
	if not args.dry_run:
		print("executing shell command")
		os.system(cmd)
	else:
		print("dry run, not executing command")
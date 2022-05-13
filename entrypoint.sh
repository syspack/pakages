#!/bin/bash

if [ -z "${token}" ]; then
    printf "You are required to provide a GitHub token.\n"
    exit 1
fi

# Ensure input token is defined
export GITHUB_TOKEN=${token}

if [ -z "${user}" ]; then
    printf "Please provide a user input for the username associated with the token.\n"
    exit 1
fi

# Login with user and github token
echo ${GITHUB_TOKEN} | oras login -u ${user} --password-stdin ghcr.io

if [ -z "${package}" ]; then
    printf "An input package or spec string is required to build.\n"
    exit 1
fi

# If deploy is set to true and we don't have a uri, this is an error 
if [ "${deploy}" == "true" ] && [ -z "${uri}" ]; then
    printf "If you want to deploy you must define a uri (unique resource identifier)\n"
    exit 1
fi

# Run pakages for the specs provided, with deploy or not
if [ "${deploy}" == "true" ]; then
    pakages build "${package}" --push "${uri}"
else
    pakages build "${package}"
fi

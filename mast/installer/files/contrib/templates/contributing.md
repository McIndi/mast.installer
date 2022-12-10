[Back to index](./index.html)
<h1>MAST for IBM DataPower Version {0}</h1>
<h2>Contributing Guide</h2>

[TOC]

# Introduction

This document will outline the basic flow of code and/or ideas to the MAST for IBM DataPower version 2.x.x.

We will outline a process which, when followed, will lead to a much more auditable and controlable
process for making changes to our code.

# Basics

We will list several guidelines here. It should be the goal of any contributer to follow each step in
this section.

1. Every change needs to start with an issue (the mast.installer repository is a good place to start). We will
make use of a feature of GitHub which allows us to provide our users with issue and pull-request templates.
2. The issue is where discussion should take place regarding the actual problem and possible solutions.
3. A pull request normally won't be considered until the original issue is at least 24 hours old. This
is to allow interested parties time to comment.
3. Once a solution is agreed upon, a branch should be made, the desired changes implementated and a pull
request should be submitted.
4. The pull request is where code review takes place. Normally, the pull-request will not be merged until 24 hours
has passed. This is meant to give interested parties time to submit a code review.
5. (This rule won't take effect until a comprehensive untit test solution is decided upon) Any change should have
a unit test associated with it.
6. Wherever possible we should link to/from each issue and pull request and we should use
[@mentions](https://github.com/blog/821-mention-somebody-they-re-notified)to notify
anyone who might be interested in a particular issue or pull request)
7. If you are interested in updates to our project, you should
[watch](https://help.github.com/articles/be-social/#watch-a-project)
the [mast.installer](https://github.com/mcindi/mast.installer) project.

# Building

## Requirements

You must have the following software installed and on the `PATH` on the build machine:

* Python 3.3, 3.4, 3.5, 3.6, 3.7, 3.8 and 3.9
* pyinstaller
* git (optional, but recomended for automated builds)

## building

1. clone repository `git clone --recursive https://github.com/mcindi/mast.installer`
2. Change directory `cd mast.installer/mast/installer`
3. Execute build script `python build.py`
4. The installation binary will be in a subdirectory called `dist`

## Installing

To install simply place the installer in a directory and execute.

For more advanced installation options you can execute installer from a
command line and pass in the `--help` flag.

## Running tests

The tests can be run with the utility `test-mast.bat -A`.

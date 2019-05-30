[Back to index](./index.html)
<h1>MAST for IBM DataPower Version {0}</h1>
<h2>Getting Started Guide</h2>

[TOC]

# Introduction

Welcome to the MAST for IBM DataPower Getting Started Guide. In this guide
we will cover some basic configuration and use of MAST for IBM DataPower.
Please note, however, that upon installation MAST for IBM DataPower is ready
for use, but to make the product easier to use and to maximize your investment
in the product some simple configuration will help.


NOTE: Throughout this document we will refer to $MAST_HOME, please be advised
that this will refer to the directory into which MAST was installed

# First thing first

While there are a few different ways in which MAST can be secured, the most
obvious one and the most necessary one is to replace the default key-pair
which comes with MAST. While you can go with a signed certificate, it is not
necessary, but what is absolutely necessary is to replace the pair that comes
with MAST. This is because this is the same key-pair which ships with all MAST
products. We include it so that MAST can be up and running over TLS upon
installation, but anyone remotely familiar with MAST will be able to easily
decrypt your traffic if you do not change the default key pair.

# Configuring your hosts

One of the more useful features of MAST is that you can define aliases for
your appliances which you can use with any of MAST's other features. In order
to configure your aliases it will be necessary to copy the file
`$MAST_HOME/etc/default/hosts.conf` to `$MAST_HOME/etc/local/hosts.conf`
and edit the file in the local directory.

This file is meant to consist of one stanza of the following format:

    :::ini
    [hosts]
    alias_1: hostname_or_ip_1
    alias_2: hostname_or_ip_2

So for instance if you have three environments with two DataPower appliances
each:

* dev (10.0.1.1, and 10.0.1.2)
* qa (10.1.1.1 and 10.1.1.2)
* prod (10.2.1.1 and 10.2.1.2)

Then you could create a stanza like the following:

    :::ini
    [hosts]
    dev_dp_1: 10.0.1.1
    dev_dp_2: 10.0.1.2
    qa_dp_1: 10.1.1.1
    qa_dp_2: 10.1.1.2
    prod_dp_1: 10.2.1.1
    prod_dp_2: 10.2.1.2

Then whenever you use mast to administer your appliances, you can refer to
them by their aliases. so if you want to reference the two appliances in prod
you can say prod_dp_1 and prod_dp_2.  Using this feature allows your
organization to keep its existing dns or ip addressing scheme while giving
your administrators and developers a way to use more contextual names to refer
to your appliances.

# Configuring your Environments

Another useful feature of MAST is to allow you to define arbitrary groups of
appliances. Using the example above it would be useful to define four environments:

* dev
* qa
* prod
* all

This way if you need to affect all the appliances in any of these environments
you can simply specify the environment name and mast will reach out to all
of the appliances defined within that environment.

In order to configure your environments, it will be necessary to copy the
file `$MAST_HOME/etc/default/environments.conf` to
`$MAST_HOME/etc/local/environments.conf` and edit the file in the local
directory. This file should consist of a stanza for each environment
with the following format:

    :::ini
    [ENVIRONMENT_NAME]
    appliances: hostname_or_ip_1 hostname_or_ip_2 ...

It should be noted that you can use aliases defined in your hosts.conf here
instead of the actual hostname or IP Address. So, if we have the hosts.conf
as defined above, we could configure our environments like this:

    :::ini
    [dev]
    appliances: dev_dp_1 dev_dp_2

    [qa]
    appliances: qa_dp_1 qa_dp_2

    [prod]
    appliances: prod_dp_1 prod_dp_2

    [all]
    appliances: dev_dp_1 dev_dp_2 qa_dp_1 qa_dp_2 prod_dp_1 prod_dp_2

Now if you need to affect both appliances in prod, you can simply
provide `prod` as the hostname

# Configuring the Server

Since the MAST Web GUI is a hosted web app, it is possible to configure
certain options related to the server. The available options are well
documented within the file `$MAST_HOME/etc/default/server.conf` but some
of the most important ones are under the [server] stanza. Here you can set
the listening host and port as well as the private key and public certificate
also in this stanza you can specify secure which is corresponds to whether or
not to use TLS. Please see the documentation in server.conf.

# Configuring Logging

There are a few options you can use to configure the logging of MAST. Please
see the documentation in logging.conf on what the various options mean.

# Basic Usage

NOTE: We will be using the configurations we defined above, specifically
the environments.conf and hosts.conf in order to make the examples more
concise.

NOTE: Although we will not include it in the commands, if you have not
replaced the key pair for the xml management interface, or the key-pair
is not in your system's trust-store, you will need to add a "-n" to each
of these commands to disable hostname verification.

We will cover some basic usage of MAST here, but for more details see the
[CLI Reference](/CLIReference.html) and the [API Reference](/APIReference). We
will go over some common use-case scenarios and complete them using the CLI.
Here are the scenarios we will cover:

* Add a user to all appliances, and force them to change their password on login
* Add a domain to a group of appliances
* Import a configuration ZIP file into a group of appliances

## Adding a User

Our use case is this:

A new developer has joined our team, and we need to add a user to the dev
DataPower appliances and associate this user with the developer group

In order to list the users we currently have on the appliances, we can
issue the following command:

    :::bash
    $ ./mast-accounts list-users -a all -c username:password
    dev_dp_1
    ========
    user_1
    user_2
    user_3

    dev_dp_2
    ========
    user_1
    user_2
    user_3
    user_4

    common
    ======
    user_1
    user_2
    user_3

We can see here that there is one user which only exists on the dev_dp_2
appliance. This may or may not be purposeful (and I've just included it here
to demonstrate how we would see something like that). For our task, however,
this is irrelevant. We need to add the new user to the dev appliances. We can
do that with the following command:

    :::bash
    `$ ./mast-accounts add-user -a dev -c username:password -u new_user -p pa55word -g developer -s`

This will add a user to both dev appliances and associate them with the
developer group. We can then verify that it was added by listing the users
just as we did above:

    :::bash
    `$ ./mast-accounts list-users -a all -c username:password`
    dev_dp_1
    ========
    user_1
    user_2
    user_3
    new_user

    dev_dp_2
    ========
    user_1
    user_2
    user_3
    user_4
    new_user

    common
    ======
    user_1
    user_2
    user_3
    new_user

The "-s" flag to the add-users command told MAST to save the configuration
after the user was added, so we could stop here, but we should probably
ensure that our new user needs to change their password on the next login. We
can do that with the following command:

    :::bash
    `$ ./mast-accounts force-change-password -a dev -c username:password -U new_user`

Now when the new user goes to log onto the appliance, they will be forced to
change their password. That concludes our first use case, now we will look at
adding a domain to a group of appliances.

## Adding a Domain

Our use case is this:

We have a new application which is starting out in the dev environment. We
would like a new domain where our developers can work on the configurations
and services which will make up this application.

So probably the first thing we should do is look at which domains exist on
our development appliances. We can do that with the following command:

    :::bash
    $ ./mast-system show-domains -a dev -c username:password
    dev_dp_1
    ========
    default
    domain_1
    domain_2

    dev_dp_2
    ========
    default
    domain_1
    domain_2
    domain_3

    common
    ======
    default
    domain_1
    domain_2

We can see again that dev_dp_2 has one domain that doesn't exists on dev_dp_1,
but that's not our concern right now. We need to add a domain named new_domain
to both boxes. We can do that with the following command:

    :::bash
    `$ ./mast-system add-domain -a dev -c username:password -d new_domain -s`

This will add our domain and the "-s" flag will cause MAST to save the
configuration. Now all that is left to do is to list all the domains again,
just to be sure that it was added.

    :::bash
    `$ ./mast-system show-domains -a dev -c username:password`
    dev_dp_1
    ========
    default
    domain_1
    domain_2
    new_domain

    dev_dp_2
    ========
    default
    domain_1
    domain_2
    domain_3
    new_domain

    common
    ======
    default
    domain_1
    domain_2
    new_domain

As we can see our new domain is now on both boxes. Next we will look at how to
import a configuration ZIP file into our new domain.

## Importing Configuration

So, we have our new developer and we created a new application domain for her
new project. Now our new developer is so eager to begin that she has already
created her first new service in preparation of her new application. It is our
task to import the configuration into our dev environment. We can do that with
this command:

    :::bash
    `$ ./mast-developer import -a dev -c username:password -D new_domain -f ~/Downloads/export.zip`

Now, there is a reason that this command does not persist the changes and that
is to give the interested parties a chance to "check-out" the results. Once
that's done, you can save the configuration with the following command:

    :::bash
    `$ ./mast-system save -a dev -c username:password -D new_domain`

That's it, simple really, but this is all in dev. There are a lot more
restrictions about making changes in our qa and prod environments.

# Conclusion

That concludes our getting started guide. Please contact [support@mcindi.com](mailto://support@mcindi.com)
if you have additional questions about getting started.

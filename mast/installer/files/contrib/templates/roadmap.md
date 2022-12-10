[Back to index](./index.html)
<h1>MAST for IBM DataPower Version {0}</h1>
<h2>Release Notes</h2>

[TOC]

# Introduction

In this document we will keep track of where we are heading for the future of
MAST. We will concentrate on features, enhancements and known-issues. Also,
we will try to outline and explain our rationale for the decisions we have
made in the past as well as decisions which we are currently making.

# Major Milestones

* Version 1 - Complete
    * Create a viable product which eases the common pains of administrating
    IBM DataPower appliances.
    * Ease the process of querying, configuring or otherwise affecting multiple
    IBM DataPower appliances as a group.
    * Create a system for allowing robust configuration without any additional pains
    and with a minimal learning curve for future contributers
    * Create a CLI from functions based on their signature
    * Dynamically generate a Web GUI from our CLI
    * Provide an easy-to-use Python API for creating custom plugins and scripts
    * Provide a plugin system for use with the Web GUI
    * Provide an easy-to-use installer for Linux and Windows
* Version 2 - Complete
    * Provide a daemon on Linux and a Service on Windows (mastd) with
    a plugin system which allows users/contributers to host threads
    performing tasks based on their environment
    * Use the daemon to host the MAST Web GUI
    * Use the daemon to host a cron-style scheduler
    * Switch to using the Anaconda Python Distribution which provides many benifits including
        * The Anaconda Python distribution is the fastest growing data analytics platform
        today, and we believe that brining these analytics capabilities to the areas
        of systems administration, operations and development will be key to taking full
        advantage of the capabilities of our systems.
        * The Anaconda Python distribution comes packaged with a number of utilities
        and libraries whose installation are common pain-points for organizations
        looking to adopt Python
            * py.test - A simple no-boilerplate testing framework
            * spyder - A Python IDE useful for extending MAST's functionality
            * IPython - An enhanced Python terminal useful for exploring MAST's
            Python API
            * IPython notebook - An interactive computational environment, in
            which you can combine code execution, rich text, mathematics, plots
            and rich media.
            * Python libraries to interact with Excel
            * pandas - A library for data manipulation and analysis
            * bokeh - An interactive visualization library that targets modern
            web browsers for presentation
        * And tons more, see [why anaconda](https://www.continuum.io/why-anaconda)
    * Bring a unified logging system based on Python's standard logging
    module to simplify the process of getting logs where they need to go
    * Focus on stabilization
* Version 2.0.1 - Complete
    * Start integrating Anaconda's capabilities in with contributed
    scripts which are not part of the core product for reasons of portability
    * Focus on bug fixes, documentation and stabilization
    * Start the process of decoupling MAST from MAST for IBM DataPower so
    each project can focus on their primary concern
* Version 2.1.0 - Complete
    * Bring in the Python library [dulwich](https://github.com/jelmer/dulwich)
    for native git integration, we have a number of uses for this functionality
        * Configuration (persisted and/or running) auditing
            * This is partially achieved in two POC contrib
            scripts `track-autoconfig.py` and `track-getconfig.py`
        * Power our "net-install" feature which clones the latest versions
        of all our dependent libraries and installs them during installation
        * Power our `build-hotfix.py` contrib script which allows our
        users to update MAST with a single command as well as build a
        hotfix which can be deployed to machines without internet access
        * Integration with git for deployment automation
        * Integrate a git server with mastd as a plugin
    * Focus on documentation
        * In particular, we have overhauled the process of generating our
        documentation.
            * Our documentation is now auto-generated from our source code
            and a couple of markdown files. This allows our users to update
            our product and generate the updated documentation on-the-fly
    * Focus on bug fixes and stability
* Version 2.2.0 - Complete
    * Remove dependency on dulwich due to lack of support, although they are
    working on the issues, we need certain features to work
    * Focus on usability and bug fixes
    * Dynamically populate version throughout product to help with
     troubleshooting
    * Lots more, please check out our [release notes](./releasenotes.html)
* Version 3.0.0
    * Migrate to Python 3
        * Python 2 support will end January 2020, so we need to migrate to
        Python 3.7.
* Version3.1.0
    * Improve the process of contributing to our projects
        * Adopt a better, more modern development workflow
        really utilizing GitHub and all of it's community
        based features
    * Finish the process of decoupling MAST from MAST for IBM DataPower
    and start a couple of new projects like:
        * MAST for docker
        * MAST for Linux
        * MAST for Windows
    * Rewrite the Web GUI to have a more useful, modern UI
* Version 4
    * The sky is the limit, we will continue to develop our product
    based on the needs of our new and existing customers and community

# Conclusion

This document is living and breathing, please check back to see updates
to this document which will outline our direction for the future.

# tbpweb
TBP CA-A website rework, build in Django

## Setup 

**Vagrant** will automatically setup a virtual machine with the correct
setup for developing `hknweb`.

Install [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
It is okay to install the latest of both (and mostly recommended)! Otherwise, consult with another Officer who has the setup working and first try to match the VirtualBox version and then the Vagrant version.

*In one point in time, there have been some issues in the past with other versions of Virtual Box in terms of compatibility of Vagrant.
You can find those here [VirtualBox Old 6.0 Builds](https://www.virtualbox.org/wiki/Download_Old_Builds_6_0), and at the time, Virtual Box 6.0.14 was recommended*

Fork the tbpweb repository and clone your fork to your local machine 

Open terminal, and cd into the cloned directory (if on Windows, be sure to run Command Prompt instead, as administrator). Check to make sure there is a Vagrantfile in the directory. If on Windows, also run VirtualBox as admin. Then, from the cloned directory in terminal, type

```sh
$ vagrant up
```

which will download and boot a Linux virtual machine, then run setup.

To access the environment, run

```sh
$ vagrant ssh
```

which will `ssh` your terminal into the virtual machine.

See [Development](#development) for how to run the Django web server.

From here, run

```sh
$ cd tbpweb
```

Developing on `tbpweb` requires a virtual environment so that every developer has the exact same development environment i.e. any errors that a developer has is not due to difference in configuration. We will be using Python's built-on [`venv`](https://docs.python.org/3/library/venv.html) to make our virtual environment. This command creates our virtual environment.

```sh
$ make venv
```

Next, we need to have our current terminal/shell use the virtual environment we just created. We do this through:

```sh
$ source .venv/bin/activate
```

To install all dependencies (including django), run

```sh
$ make install
```
There may be warnings that installation of some packages failed, but as long as you can run the command below successfully you are good to go.

If you make any Django changes (to the database models, for instance) you will have to create and migrate migrations. You can do so with the command below. If there were changes to database models made by other developers and you pulled those changes, you just have to run make migrate.
```sh
$ make migrations
$ make migrate
```

If you would like to access the admin interface, create a superuser using the command
```sh
$ make superuser
```

Finally, to run the web instance, simply run the command

```sh
$ make run
```
This will start the development server at http://0.0.0.0:3000/. If you go into your web browser and access localhost:3000, you should be able to see the site now!

To access the admin site, access http://0.0.0.0:3000/admin. Use the credentials you created for your superuser to login.

To exit out of the pipenv shell, run 

```sh
$ exit
```
The same command can be used to exit out of the virtual machine ssh connection.

To turn off the virtual machine, run

```sh
$ vagrant halt
```

which will attempt to safely shutdown the virtual machine, or kill it otherwise.



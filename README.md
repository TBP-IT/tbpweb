# tbpweb
TBP CA-A website rework, build in Django

## Setup 

**Vagrant** will automatically setup a virtual machine with the correct
setup for developing `tbpweb`.

Install [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_6_0)
Make sure you install Virtual Box 6.0.14, as Vagrant is not compatible with newer versions of Virtual Box.


Fork the tbpweb repository and clone your fork to your local machine 

Open terminal, and cd into the cloned directory. Check to make sure there is a Vagrantfile in the directory. From there, type

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

Make sure pipenv is installed in your virtual machine. To do this, run 

```sh
$ pip3 install pipenv
```

Next, make sure there is a Pipfile in your current directory and run

```sh
$ pipenv shell
```

To install django, run

```sh
$ pipenv install django
```
There may be warnings that installation of some packages failed, but as long as you can run the command below successfully you are good to go.

If you edit any database models, you will have to create and apply migrations. You can do so with the following commands:

```sh
$ make migrations
$ make migrate
```

Finally, to run the web instance, enter the command

```sh
$ make run
```
or alternatively

```sh
$ make
```
(since run is the first recipe in the Makefile).

If you go into your web browser and access localhost:3000, you should be able to see the site now!

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



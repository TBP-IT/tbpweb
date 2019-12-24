# tbpweb
TBP CA-A website rework, build in Django

## Setup 

**Vagrant** will automatically setup a virtual machine with the correct
setup for developing `hknweb`.

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
$p ipenv shell
```
Finally, to run the web instance, you should have a file in the directory called maange.py

Run the command

```sh
$ python3 manage.py runserver
```
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



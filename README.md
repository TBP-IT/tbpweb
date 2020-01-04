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
which will download and boot a Linux virtual machine, then run setup. If you need to force setup again, run 

```sh
$ vagrant provision
```
Do not do this if `vagrant up` works as intended (i.e. you can properly follow the below steps to generate a web instance).

You can check the state of the VM by running

```sh
$ vagrant status
```

To access the environment, run

```sh
$ vagrant ssh
```
which will `ssh` into the virtual machine.

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

If you make any Django changes (to the database models, for instance) you will have to create migrations to reflect them. You can do so with the command
```sh
$ make migrations
```

After, you should migrate the migrations. If there were changes to database models made by other developers and you pulled those changes, you have to apply the migrations as well. This can be done with the command:
```sh
$ make migrate
```

If you would like to access the admin interface, create a superuser using the command
```sh
$ make superuser
```
You will be prompted to enter a username and password which can be used to log in to the admin interface. 

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



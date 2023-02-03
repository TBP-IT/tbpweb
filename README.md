# tbpweb
TBP CA-A website, built in Django

## Prerequisites

For a more detailed explaination and instruction on what to install, see the [Setup's Prerequisites section](https://github.com/TBP-IT/tbpweb/wiki/Setup#prerequisites)

In summary, you need the following installed:
* `git`
* Any `sh` shell (e.g. `bash`, `zsh`, etc.) / `Git Bash` on Windows
* Miniconda (or Anaconda)
* Ruby (OCF uses 2.7.7, but we can use 3.1.X) (Windows should use `Ruby+Devkit`)
    * Install "Compass": `gem install compass -v 1.0.3`

## Setup and Development

For a more detailed explaination and breakdown, see the [Setup Wiki](https://github.com/TBP-IT/tbpweb/wiki/Setup)

Fork the tbpweb repository and clone your fork to your local machine

All commands must be ran on a `sh` shell

In summary, the commands you will use are (in general this order):
```sh
$ cd tbpweb                                     # enter our main directory
$ conda env create -f config/tbpweb-dev.yml     # create our Conda Environment and install dependencies
$ conda activate tbpweb-dev                     # enter our Conda Environment
$ python manage.py makemigrations               # Create migrations files
$ python manage.py migrate                      # apply all database changes
$ python manage.py runserver 0.0.0.0:3000       # start local web server
$ conda deactivate                              # Exit the Conda Environment
```

You may choose to remove the development environment by running: `conda env remove --name tbpweb-dev`

### Development

To run the Django development server (which runs a web server locally), run
```sh
$ python manage.py runserver 0.0.0.0:3000
```
which will make the web site available at `http://localhost:3000`.

If you would like to access the admin interface in the local web server, run
```sh
$ python manage.py createsuperuser
```

You will be prompted for some login info, after which you should be able to access the admin interface with your super user credentials at `http://localhost:3000/admin`.

If there are development conflicts between Operating System, a solution that works on Linux takes precedence (as the destination OS on Berkeley's OCF)! Unix developers should also try to make their code Windows-friendly for the Window developers.

## Deploy

Make sure all changes to be pushed are in `tbpweb`'s `master` branch

Deploy by running `fab --prompt-for-login-password deploy` in the Conda Environment and enter the TBP OCF password

Other fabfile commands (including rollback) here: https://github.com/TBP-IT/tbpweb/wiki/Deployment

## Various links to understand some of the code structure and tools

* fixtures/*.yaml -- https://docs.djangoproject.com/en/2.2/howto/initial-data/

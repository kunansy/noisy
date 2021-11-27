
# Noisy
[![CircleCI](https://circleci.com/gh/1tayH/noisy/tree/master.svg?style=shield)](https://circleci.com/gh/1tayH/noisy/tree/master)

A simple python script that generates random HTTP/DNS traffic noise in the background while you go about your regular web browsing, to make your web traffic data less valuable for selling and for extra obscurity.

Noisy is expected to be executed in Docker, OS doesn't matter.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine

### Usage

Clone the repository
```
git clone https://github.com/1tayH/noisy.git
```

Run the container

```
docker-compose up -d --build --force-recreate
```

###  Output
```
$ NOISY_DELAY=30 TIMEOUT=120 docker-compose up --build --force-recreate
INFO    [2021-11-27 14:54:20,427] [crawl():203] Noising started
DEBUG   [2021-11-27 14:54:21,729] [request():31] http://4chan.org: requesting
DEBUG   [2021-11-27 14:54:22,830] [request():39] http://4chan.org: response received
DEBUG   [2021-11-27 14:54:22,842] [crawl():212] http://4chan.org: found 104 links
DEBUG   [2021-11-27 14:54:23,724] [request():31] https://wikipedia.org: requesting
DEBUG   [2021-11-27 14:54:24, 95] [request():39] https://wikipedia.org: response received
DEBUG   [2021-11-27 14:54:25,741] [request():31] https://instagram.com: requesting
DEBUG   [2021-11-27 14:54:26,825] [request():39] https://instagram.com: response received
DEBUG   [2021-11-27 14:54:50,740] [request():31] https://google.com: requesting
DEBUG   [2021-11-27 14:54:51, 65] [request():39] https://google.com: response received
DEBUG   [2021-11-27 14:54:54,742] [request():31] https://google.com: requesting
DEBUG   [2021-11-27 14:54:54,986] [request():39] https://google.com: response received
DEBUG   [2021-11-27 14:54:54,993] [crawl():212] https://google.com: found 8 links
INFO    [2021-11-27 14:54:54,993] [crawl():222] Timeout has exceeded, exiting
...
```

## Some examples

Some edge-cases examples are available on the `examples` folder. You can read more there [examples/README.md](examples/README.md).

## Authors

* **Itay Hury** - *Initial work* - [1tayH](https://github.com/1tayH)
 
See also the list of [contributors](https://github.com/1tayH/Noisy/contributors) who participated in this project.

## License

This project is licensed under the GNU GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

This project has been inspired by
* [RandomNoise](http://www.randomnoise.us)
* [web-traffic-generator](https://github.com/ecapuano/web-traffic-generator)
* [cronn](https://github.com/umputun/cronn) – a simple cron for containers.

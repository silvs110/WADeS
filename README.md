<div align="center">
    <h1 align="center">WADeS</h1>
    <p align="center">
    An intrusion detection system that detect anomalies by analyzing the resources used by the applications running in the 
    system.
    <br />
    <a href="https://github.com/silvs110/WADeS/issues">Report Bug</a>
    ·
    <a href="https://github.com/silvs110/WADeS/issues">Request Feature</a>
    </p>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GPL v3.0 License][license-shield]][license-url]

</div>


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#disclaimer">Disclaimer</a></li>
  </ol>
</details>

## About The Project
WADeS or Workload Anomaly Detection System is an intrusion detection system that uses workload resource usage to
identify abnormal behaviour. This tool models the following process attributes using a frequency approach:
* cpu usage
* memory usage
* child processes count
* opened files
* users (owners)
* number of threads
* number of IPv4 and IPv6 connections

## Prerequisites
1. Python 3.8 +
2. Linux (Ubuntu)

## Installation
Note: You need to have root permission to install this tool.
1. Download the code.
2. Change the configurations in `wades_config.py`. This step is optional, unless you want to interact with WADeS. 
   In that case, change the value of `run_modeller_server` to True.   
3. Run `setup_and_start.sh` to create, install and run the background daemons. (You have to input your password).
4. To interact with WADeS, run `python3 src/main/wades.py`

## Usage
The following commands are supported by WADeS:
#### Modeller
* `modeller start` -  Starts the modeller daemon.
* `modeller terminate` - Stops the modeller daemon.
* `modeller status` - Gives you the status of the modelling process.
* `modeller pause` - Pauses the modelling process.
* `modeller continue` - Continues the modelling process.

#### ProcessHandler
* `pshandler start` - Starts the pshandler daemon.
* `pshandler terminate` - Stops the pshandler daemon.

#### Modelled apps
* `modelled apps` - Gets a list of modelled applications. This list only includes running applications.
* `abnormal apps` - Gets a list of abnormal applications that were found in the current modelling process. 
  To view all the abnormal applications found add `--history`.

<!-- LICENSE -->
## License

Distributed under the GPL license v3.0. See [`LICENSE`](https://github.com/silvs110/WADeS/blob/main/LICENSE) 
for more information.

## Disclaimer

This product does not come with a warranty. It is build as part of research project and it should be safe
to run on your system, but we make no claims with respect of functionality.

[contributors-shield]: https://img.shields.io/github/contributors/silvs110/WADeS.svg?style=for-the-badge
[contributors-url]: https://github.com/silvs110/WADeS/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/silvs110/WADeS.svg?style=for-the-badge
[forks-url]: https://github.com/silvs110/WADeS/network/members
[stars-shield]: https://img.shields.io/github/stars/silvs110/WADeS.svg?style=for-the-badge
[stars-url]: https://github.com/silvs110/WADeS/stargazers
[issues-shield]: https://img.shields.io/github/issues/silvs110/WADeS.svg?style=for-the-badge
[issues-url]: https://github.com/silvs110/WADeS/issues
[license-shield]: https://img.shields.io/github/license/silvs110/WADeS.svg?style=for-the-badge
[license-url]: https://github.com/silvs110/WADeS/blob/master/LICENSE



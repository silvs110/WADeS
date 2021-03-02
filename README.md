<div align="center">
    <h1 align="center">wades</h1>
    <p align="center">
    An intrusion detection system that detect anomalies by analyzing the resources used by the applications running in the 
    system.
    <br />
    <a href="https://github.com/silvs110/wades/issues">Report Bug</a>
    ·
    <a href="https://github.com/silvs110/wades/issues">Request Feature</a>
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
wades or Workload Anomaly Detection System is an intrusion detection system that uses workload resource usage to
identify abnormal behaviour. This tool models the following process attributes using a frequency approach:
* CPU usage
* Memory usage
* Child processes count
* Opened files
* Users (owners)
* Number of threads
* Number of open sockets

## Prerequisites
1. Python 3.8+
2. Linux (Ubuntu)

## Installation
Note: You need to have root permission to install this tool.
1. Download the code.
2. Change the following configurations in **wades_config.py**:
   * `is_test` to `False`
   * `run_modeller_server` to `True`. This step is optional, but it is needed for retrieving the modelled data.
3. Run **set_up_wades_service.sh** to create, install and run the background daemon. (You have to input your password). 
   The tool should start automatically after the script finishes executing.

## Usage
To interact with wades run: `python3 wades.py <command>`.
Supported commands:
* `start` - Starts wades daemon.
* `stop` - Stops wades daemon.
* `modeller status` - Gives you the status of the modelling process.
* `modeller pause` - Pauses the modelling process.
* `modeller continue` - Continues the modelling process.
* `modelled apps` - Gets a list of modelled applications. This list only includes running applications.
* `abnormal apps` - Gets a list of abnormal applications that were found in the current modelling process. 
  To view all the abnormal applications found add `--history`.
* `help` - Gets a list of supported commands.
<!-- LICENSE -->
## License

Distributed under the GPL license v3.0. See [`LICENSE`](https://github.com/silvs110/wades/blob/main/LICENSE) 
for more information.

## Disclaimer

This product does not come with a warranty. It is build as part of research project. It should be safe
to run on your system, but we make no claims regarding functionality.

[contributors-shield]: https://img.shields.io/github/contributors/silvs110/wades.svg?style=for-the-badge
[contributors-url]: https://github.com/silvs110/wades/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/silvs110/wades.svg?style=for-the-badge
[forks-url]: https://github.com/silvs110/wades/network/members
[stars-shield]: https://img.shields.io/github/stars/silvs110/wades.svg?style=for-the-badge
[stars-url]: https://github.com/silvs110/wades/stargazers
[issues-shield]: https://img.shields.io/github/issues/silvs110/wades.svg?style=for-the-badge
[issues-url]: https://github.com/silvs110/wades/issues
[license-shield]: https://img.shields.io/github/license/silvs110/wades.svg?style=for-the-badge
[license-url]: https://github.com/silvs110/wades/blob/master/LICENSE



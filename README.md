# Cansync

<!--toc:start-->
- [Cansync](#cansync)
  - [Features](#features)
  - [Usage](#usage)
  - [Installation](#installation)
  - [Contribution](#contribution)
<!--toc:end-->

All-in-one manager for _educational resources_ hosted on **Canvas**.

## Features

- Download all resources (e.g. files, text, etc.)
- Manage courses and accounts
- Synthesize new resources (e.g. problem sheets) using LLMs

## Usage

```sh
$ cansync download
Downloading all files...
Finished in 5.0s.
$ cansync courses
(10848) Data Structures & Algorithms
(91842) Software Engineering
(59283) Functional Programming
$ cansync download 10848
Downloading all files from Data Structures & Algorithms
Finished in 2.0s.

```

## Installation

Arch:
`` yay -S python-cansync ``

Basically anything else:

1. Install [uv](https://github.com/astral-sh/uv)
`` uv tool install cansync ``

## Contribution

yes

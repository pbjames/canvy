# Canvy

<!--toc:start-->
- [Canvy](#canvy)
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
$ canvy download
Downloading all files...
Finished in 5.0s.
$ canvy courses
(10848) Data Structures & Algorithms
(91842) Software Engineering
(59283) Functional Programming
$ canvy download 10848
Downloading all files from Data Structures & Algorithms
Finished in 2.0s.
$ canvy teacher
>>> read the mle file and tell me about the urn example
INFO Reading: W2
┏━ Message          ━┓
                                                              
  read the mle file and tell me about the urn example         
                                                              
┏━ Tool Calls       ━┓
                                                              
  • canvas_files()                                            
  • retrieve_knowledge(pdf_rel_path=LI Artificial Intellig    
  Materials/W2.1-MLE.pdf)                                     
                                                              
┏━ Response (12.8s) ━┓
                                                              
  The urn example in the "W2.1-MLE.pdf" file is a classic     
                                                              
  Here's the essence of the urn example:                      
                                                              
  - There is an urn with two types of balls: red balls ...    
  - The proportion of red balls in the urn is unknown, ...    
  ...                                                         
                                                              
  The example demonstrates how MLE uses observed data to i    
  simple and concrete scenario. If you want, I can provide    
                                                              
INFO Loading knowledge base
INFO Loaded 24 documents to knowledge base
>>>
```

## Installation

Arch (not yet):
``yay -S python-canvy``

Basically anything else:

1. Install [uv](https://github.com/astral-sh/uv)
2. ``uv tool install canvy``

## Contribution

yes

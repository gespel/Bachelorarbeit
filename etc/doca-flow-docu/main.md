# DOCA Flow

## Introduction

DOCA Flow is the API Nvidia made in order to make use of the proclaimed hardware offload. As opposed to the other libraries and frameworks in doca, flows goal is to modify packets specifically. The architecture might be best described as almost fully declerative. It is comparable to yaml or json files used define ressource in kubernetes and docker for example. DOCA Flows library is written in C thus providing us a C only API. Obviously C is turing-complete but DOCA Flow is not! In using the API we basically write a glorified configuration file

## Syntax
The DOCA header provides us most function names and data structure that can be used. The problem is that the function definitions are hidden from us in the form of precompiled libraries. So in order to understand most of the functionality the only tool left to us is brute force and starring at the code. Most functions start with
`doca_flow_*`

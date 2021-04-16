# headpose_expressions_estimation_face-api

## Overview

This web application extracts facial landmarks and predict facial expression on client side using face-api.js. The 2D facial landmarks are used to estimate headpose uisng Levenberg-Marquardt optimization. 

## Setup

* Clone Repository

``` bash
git clone https://github.com/jiamingli9674/headpose_expressions_estimation_face-api.git
```

* Install Flask

```bash
pip install flask
```

* Host Website

```bash
cd headpose_expressions_estimation_face-api
python app.py
```

* Access it @ [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
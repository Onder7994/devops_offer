#!/bin/bash

docker run -d --network host -p 8085:8085 --env-file .env devops_offer
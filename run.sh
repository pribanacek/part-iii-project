#!/bin/bash
docker run -it \
    -v ~/Cambridge/Part\ III\ Project/part-iii-project/src:/src\
    -v ~/Cambridge/Part\ III\ Project/part-iii-project/src/db:/docker-entrypoint-initdb.d\
    --name=user-0 --network intermediary-network \
    data_intermediary:latest bash

# Beta AI

Beta AI is a React Native App that connects to a Flask server to find the beta for indoor bouldering routes

## Description

This is beta solver for indoor bouldering routes. We trained models to recognize holds on a wall, and also predicted their difficulty. We used numpy arrays to get the dominant color of the hold and use it to create routes of the same colored holds. We then ran a search algorithm on the route with a given starting and finishing holds to then find an optimal route up the wall. 

I connected this to a React Native App made in expo so both Android and iPhone users can use it more easily.

## Getting Started

### Dependencies

- Node Package Manager
- Expo Go on either Android or iPhone

### Installing

* Fork this repository
* run `npm install` in the main file to install dependencies
* That's it

### Executing program

To start both the server and the app:
```
cd frontend/beta
npx expo start
cd backend/server.py
```
and run this file
* Make sure you edit the ipaddress in CameraComponent.tsx so that it calls the right server API
* This ipaddress should be the same one you see in the browser in the flask server and also after running `npx expo start`

## Authors
- [@LiamEvans](https://github.com/snavemail)
- [@LiamLangert](https://github.com/LiamLangert)
- [@DanielBlauvelt](https://github.com/danielblauvelt)

## Version History

* 1.1
    * Initial Release

## License

This project is licensed under the **Liam Evans** License

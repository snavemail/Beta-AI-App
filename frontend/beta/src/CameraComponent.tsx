import React, { useState, useRef, useEffect } from 'react';
import { View, Text, Image, StyleSheet, Platform, Dimensions } from 'react-native';
import { IconButton, MD3Colors } from 'react-native-paper';
import { Camera } from 'expo-camera';
import { TouchableOpacity } from 'react-native';
// import * as ImagePicker from 'expo-image-picker';
import * as ImagePicker from 'expo-image-picker'
import Indicator from './Indicator';
import * as Permissions from 'expo-permissions';


/**
 * Asks for camera and image library access
 * Renders a camera view if there is no image selected, then if either
 * image is taken or selected, it runs the image through a model through a flask server.
 * @returns A ui for the camera component
 */
export default function CameraComponent() {
  const [hasCameraPermission, setHasCameraPermission] = useState<boolean | null>(null);
  const [image, setImage] = useState<string | null>(null);
  const [buttonDisabled, setButtonDisabled] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const cameraRef = useRef<Camera | null>(null);
  const address = '10.0.0.153'

  /**
   * Request access for camera
   */
  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasCameraPermission(status === 'granted');
    })();
  }, []);

  /**
   * Request media library access for user's image library
   */
  useEffect(() => {
    (async () => {
      if (Platform.OS !== 'web') {
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (status !== 'granted') {
          alert('Sorry, we need camera roll permissions to make this work!');
        }
      }
    })();
  }, []);

  // TODO: Change ui
  if (hasCameraPermission === null) {
    return <View><Text>Requesting camera permission...</Text></View>;
  }

  // TODO: Change ui
  if (hasCameraPermission === false) {
    return <View><Text>No access to camera</Text></View>;
  }

    /**
   * Sends a fetch request to post the current image 
   * Image is processed by the current uri, either from taking a photo
   * or choosing a photo
   * Then calls get request to receive the resulting image
   * @param uri this is the uri that is used for the image source
   */
    const processImage = async (uri: any) => {
      const file = await fetch(uri);
      const blob = await file.blob();
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result;
        const formData = new FormData();
        formData.append('image', base64 as string);
    
        fetch(`http://${address}:3000/predict-difficulty`, {
          method: 'POST',
          body: formData,
          headers: { 'Content-Type': 'image/jpeg', },
        })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          const timestamp = Date.now();
          const url = `http://${address}:3000/get-image?timestamp=${timestamp}`
          setImage(url);
          setButtonDisabled(false);
          setIsLoading(false);
        })
        .catch(error => {
          console.error('Error sending image to server:', error);
          setImage(uri);
          setButtonDisabled(false);
          setIsLoading(false);
        });
      };
      reader.readAsDataURL(blob);
    }

  /**
   * Sends a fetch request to post the current image 
   * Image is processed by the current uri, either from taking a photo
   * or choosing a photo
   * Then calls get request to receive the resulting image
   * @param uri this is the uri that is used for the image source
   */
  const processRouteImage = async (uri: any) => {
    const file = await fetch(uri);
    const blob = await file.blob();
    const reader = new FileReader();
    const hsvrList = [210, 10, 30, 30];
    reader.onloadend = () => {
      const base64 = reader.result;
      const formData = new FormData();
      formData.append('image', base64 as string);
      formData.append('hsvr', JSON.stringify(hsvrList));

      console.log(JSON.stringify(hsvrList));
  
      fetch(`http://${address}:3000/get-color-holds`, {
        method: 'POST',
        body: formData,
        headers: { 'Content-Type': 'image/jpeg', },
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        console.log(response.json())
        response.json()
        console.log('good')
      })
      .then(data => {
        console.log('server response', data);
        const timestamp = Date.now();
        const url = `http://${address}:3000/get-color-image?timestamp=${timestamp}`
        console.log('url', url)
        setImage(url);
        setButtonDisabled(false);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error sending image to server:', error);
        setImage(uri);
        setButtonDisabled(false);
        setIsLoading(false);
      });
    };
    reader.readAsDataURL(blob);
  }

  /**
   * Takes picture and then process it in the model via the server
   * Disables the button
   * @return nothing if the camera is not available
   */
  const takePicture = async () => {
    if (!cameraRef.current) {
      console.error('Camera not available');
      return;
    }
    setButtonDisabled(true);
    setIsLoading(true);
    const { uri } = await cameraRef.current.takePictureAsync();
    processRouteImage(uri);
  };

  /**
   * Set the image to be null
   */
  const retakePicture = () => {
    setImage(null);
  };
  
  /**
   * Go through image picker to select an image (video doesn't work, although we allow it)
   * Will remove in future possibly
   * Disables camera button as well
   */
  const pickImage = async () => {
    setButtonDisabled(true);
    setIsLoading(true);
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.All,
      allowsEditing: true,
      aspect: [4, 3],
      quality: .5,
    });

    if (!result.canceled) {
      const uri = (result.assets[0].uri)
      await processRouteImage(uri);
    } else {
      setButtonDisabled(false);
      setIsLoading(false);
    }
  };

  const screenWidth = Dimensions.get('window').width / 2;
  console.log('screenWidth', screenWidth);
  return (
    <View style={{ flex: 1 }}>
      {image ? (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          <Image source={{ uri: image }} style={{ width: screenWidth / 2}} />
          <TouchableOpacity onPress={retakePicture} style={styles.retakeButton}>
            <Text style={{ color: 'white', fontSize: 20 }}>Retake</Text>
          </TouchableOpacity>
        </View>
      ) : isLoading ? (
        <View style={styles.loadingView}>
          <Indicator/>
        </View>
      )
      : (
        <View style={{ flex: 1 }}>
        <Camera ref={cameraRef} style={{ flex: 1 }}>
          <View style={{ flex: 1, backgroundColor: 'transparent', flexDirection: 'row' }} />
          <View style={styles.bottomBar}>
            <IconButton icon={'image'} onPress={pickImage} iconColor={MD3Colors.neutral70} mode={'contained-tonal'} disabled={buttonDisabled}/>
            <IconButton icon='camera' onPress={takePicture} iconColor={MD3Colors.neutral70} mode={'contained-tonal'} disabled={buttonDisabled}/>
          </View>
        </Camera>
        
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  retakeButton: {
    position: 'absolute',
    bottom: 20,
    backgroundColor: 'blue',
    padding: 10,
    borderRadius: 10,
  },
  bottomBar: {
    backgroundColor: 'black',
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
  },
  loadingView: {
    height: '100%',
    width: '100%',
    backgroundColor: 'white',
    justifyContent: 'center',
    padding: 'auto'
  },
  loadingText: {
    color: 'white',
  }
});
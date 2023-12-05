import React, { useState, useRef, useEffect } from 'react';
import { View, Text, Image, StyleSheet, Platform, Button } from 'react-native';
import { IconButton, MD3Colors } from 'react-native-paper';
import { Camera } from 'expo-camera';
import { TouchableOpacity } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

function CameraComponent() {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [image, setImage] = useState<string | null>(null);
  const [cameraButtonDisabled, setCameraButtonDisabled] = useState<boolean>(false);
  const [imageButtonDisabled, setImageButtonDisabled] = useState<boolean>(false);
  const cameraRef = useRef<Camera | null>(null);
  const address = '10.0.0.184'

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

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

  if (hasPermission === null) {
    return <View><Text>Requesting camera permission...</Text></View>;
  }

  if (hasPermission === false) {
    return <View><Text>No access to camera</Text></View>;
  }

  const processImage = async (uri: any) => {
    const file = await fetch(uri);
    const blob = await file.blob();
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result;
      const formData = new FormData();
      formData.append('image', base64 as string);
  
      fetch(`http://${address}:3000/predict`, {
        method: 'POST',
        body: formData,
        headers: { 'Content-Type': "image/jpeg", },
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const timestamp = Date.now();
        const url = `http://${address}:3000/get-image?timestamp=${timestamp}`
        
        setImage(url);
        setCameraButtonDisabled(false);
      })
      .catch(error => {
        console.error('Error sending image to server:', error);
        setImage(uri);
        setCameraButtonDisabled(false);
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
    setCameraButtonDisabled(true);
    const { uri } = await cameraRef.current.takePictureAsync();
    processImage(uri);
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
    setCameraButtonDisabled(true);
    setImageButtonDisabled(true);
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.All,
      allowsEditing: true,
      aspect: [4, 3],
      quality: .5,
    });

    if (!result.canceled) {
      const uri = (result.assets[0].uri)
      await processImage(uri);
    }
    setImageButtonDisabled(false);
    setCameraButtonDisabled(false);
  };


  return (
    <View style={{ flex: 1 }}>
      {image ? (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          <Image source={{ uri: image }} style={{ width: '100%', height: '100%' }} />
          <TouchableOpacity onPress={retakePicture} style={styles.retakeButton}>
            <Text style={{ color: 'white', fontSize: 20 }}>Retake</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <Camera ref={cameraRef} style={{ flex: 1 }}>
          <View style={{ flex: 1, backgroundColor: 'transparent', flexDirection: 'row' }} />
          <View style={styles.bottomBar}>
            <IconButton icon={"image"} onPress={pickImage} iconColor={MD3Colors.neutral70} mode={"contained-tonal"} disabled={imageButtonDisabled}/>
            <IconButton icon='camera' onPress={takePicture} iconColor={MD3Colors.neutral70} mode={"contained-tonal"} disabled={cameraButtonDisabled}/>
          </View>
        </Camera>
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
});

export default CameraComponent;
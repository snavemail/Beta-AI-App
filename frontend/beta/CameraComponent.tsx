import React, { useState, useRef, useEffect } from 'react';
import { View, Text, Image, StyleSheet, Platform } from 'react-native';
import { Button } from 'react-native-paper';
import { Camera } from 'expo-camera';
import { TouchableOpacity } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

function CameraComponent() {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [image, setImage] = useState<string | null>(null);
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

  const takePicture = async () => {
    if (!cameraRef.current) {
      console.error('Camera not available');
      return;
    }

    const { uri } = await cameraRef.current.takePictureAsync();
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
        setImage(url)
      })
      .catch(error => {
        console.error('Error sending image to server:', error);
        setImage(uri);
      });
    };
    reader.readAsDataURL(blob);
  };

  const retakePicture = () => {
    setImage(null);
  };
  
  const pickImage = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.All,
      allowsEditing: true,
      aspect: [16, 9],
      quality: 1,
    });

    console.log(result);

    if (!result.canceled) {
      const uri = (result.assets[0].uri)
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
          setImage(url)
        })
        .catch(error => {
          console.error('Error sending image to server:', error);
          setImage(uri);
        });
      };
      reader.readAsDataURL(blob);
    }
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
        // Display the camera for taking a new picture
        <Camera ref={(ref) => (cameraRef.current = ref)} style={{ flex: 1 }}>
          <View style={{ flex: 1, backgroundColor: 'transparent', flexDirection: 'row' }}>
          </View>
          <Button icon={'camera'} onPress={takePicture} style={{ marginBottom: 40 }}>
            Pic
          </Button>
          <Button icon={'camera'} onPress={pickImage} style={{ marginBottom: 40 }}>
            Roll
          </Button>
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
});

export default CameraComponent;
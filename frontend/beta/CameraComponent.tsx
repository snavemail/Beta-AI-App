import React, { useState, useRef, useEffect } from 'react';
import { View, Text, Image, Modal, StyleSheet, SafeAreaView } from 'react-native';
import { Button } from 'react-native-paper';
import { Camera } from 'expo-camera';
import * as FileSystem from 'expo-file-system';

function CameraComponent() {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [image, setImage] = useState<string | null>(null);
  const [response, setResponse] = useState<string | null>(null);
  const cameraRef = useRef<Camera | null>(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

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
  
      fetch('http://10.110.228.58:3000/predict', {
        method: 'POST',
        body: formData,
        headers: { 'Content-Type': 'multipart/form-data', },
      })
      .then(response => response.blob())
      .then(data => {
        console.log('Server Response:', data);
        setResponse("OK");
        const imageUrl = URL.createObjectURL(data);
        setImage(imageUrl);
      })
      .catch(error => {
        console.error('Error sending image to server:', error);
        setResponse(uri);
        setImage(uri);
      });
    };
    reader.readAsDataURL(blob);
  };

  if (hasPermission === null) {
    return <View><Text>Requesting camera permission...</Text></View>;
  }

  if (hasPermission === false) {
    return <View><Text>No access to camera</Text></View>;
  }

  return (
    <View style={{ flex: 1 }}>
        <Camera
          ref={(ref) => (cameraRef.current = ref)}
          style={{ flex: 1 }}
        >
          <View
            style={{
              flex: 1,
              backgroundColor: 'transparent',
              flexDirection: 'row',
            }}
          >

          </View>
          <Button icon={'camera'} onPress={takePicture} style={{'marginBottom': 40}}>Pic</Button>
        </Camera>
        {response && <Text>{response}test</Text>}
        {image && <Image source={{ uri: image }} style={{ width: 200, height: 200 }} />}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});


export default CameraComponent;
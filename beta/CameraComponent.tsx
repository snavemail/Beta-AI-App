import React, { useState, useRef, useEffect } from 'react';
import { View, Text, Image, Modal, StyleSheet, SafeAreaView } from 'react-native';
import { Button } from 'react-native-paper';
import { Camera } from 'expo-camera';

const CameraComponent: React.FC = () => {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [image, setImage] = useState<string | null>(null);
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
    setImage(uri);
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

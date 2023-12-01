// CameraComponent.tsx
import React, { useState } from 'react'
import { RNCamera } from 'react-native-camera'
import { View, Text, Image, Button } from 'react-native'
import axios from 'axios'

const CameraComponent: React.FC = () => {
  const [image, setImage] = useState<string | null>(null)

  const takePicture = async (camera: RNCamera) => {
    if (camera) {
      const options = { quality: 0.5, base64: true }
      const data = await camera.takePictureAsync(options)

      const formData = new FormData()
      formData.append('image', {
        uri: data.uri,
        type: 'image/jpeg',
        name: 'image.jpg',
      })

      // axios
      //   .post('http://localhost:5000/inference', formData)
      //   .then(response => {
      //     const rockClimbingHolds = response.data.rock_climbing_holds;
      //     // Use the rock climbing holds data in your search algorithm
      //     // Example: Pass the holds data to your search algorithm function
      //     const routeSolution = yourSearchAlgorithm(rockClimbingHolds);
      //     // Log or use the solution as needed
      //     console.log(routeSolution);
      //   })
      //   .catch(error => {
      //     console.error(error);
      //   });

      setImage(data.uri)
    }
  }

  return (
    <View>
      <RNCamera
        style={{ flex: 1 }}
        type={RNCamera.Constants.Type.back}
        autoFocus={RNCamera.Constants.AutoFocus.on}>
        {({ camera, status }) => {
          if (status !== 'READY') {
            return <Text>Camera not ready</Text>
          }

          return (
            <View>
              <Button
                title='Take Picture'
                onPress={() => takePicture(camera)}
              />
            </View>
          )
        }}
      </RNCamera>

      {image && (
        <Image source={{ uri: image }} style={{ width: 200, height: 200 }} />
      )}
    </View>
  )
}

export default CameraComponent

import { StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import CameraComponent from './CameraComponent';


export default function App() {
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <CameraComponent/>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});

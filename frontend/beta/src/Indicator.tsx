import * as React from 'react';
import { ActivityIndicator, MD2Colors } from 'react-native-paper';

const Indicator = () => (
  <ActivityIndicator animating={true} color={MD2Colors.deepOrange600} size={'large'} />
);

export default Indicator;
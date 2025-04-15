import { useState } from 'react';
import { View, Image, StyleSheet, Alert, Text } from 'react-native';
import PrimaryButton from '@/components/PrimaryButton';
import * as ImagePicker from 'expo-image-picker';
import useThemeColors from '@/hooks/useThemeColors';

export default function PhotoScreen() {
  const {background, text, primary, card, border, notification} = useThemeColors();
  const [photoUri, setPhotoUri] = useState<string | null>(null);

  const handlePickPhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Denied', 'Camera access is needed to take photos.');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ['images'],
      quality: 0.5,
    });

    if (!result.canceled && result.assets.length > 0) {
      setPhotoUri(result.assets[0].uri);
    }
  };

  return (
    <View style={styles.container}>
      {photoUri ? (
        <Image source={{ uri: photoUri }} style={styles.image} />
      ) : (
        <Text style={styles.placeholder}>No photo taken yet</Text>
      )}
      <PrimaryButton title="Take a Photo" onPress={handlePickPhoto} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 16 },
  image: { width: 200, height: 200, marginBottom: 20, borderRadius: 12 },
  placeholder: { marginBottom: 20, fontSize: 16, color: '#888' },
});
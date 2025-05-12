import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Dimensions, Image } from 'react-native';
import { GestureHandlerRootView, GestureDetector, Gesture } from 'react-native-gesture-handler';
import { useRouter } from 'expo-router';
import { useSharedValue, useAnimatedStyle, withTiming } from 'react-native-reanimated';
import * as MediaLibrary from 'expo-media-library';
import * as FileSystem from 'expo-file-system';
import useThemeColors from '@/hooks/useThemeColors';
import PrimaryButton from '@/components/PrimaryButton';
import { TouchableWithoutFeedback } from 'react-native-gesture-handler';
import Toast from 'react-native-toast-message';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

type ZoomableImageProps = {
  uri: string;
  onDelete: () => void;
};

export default function ZoomableImage({ uri, onDelete }: ZoomableImageProps) {
  const scale = useSharedValue(1);
  const { background, border } = useThemeColors();
  const [imageHeight, setImageHeight] = useState<number>(SCREEN_WIDTH); // default square
  const router = useRouter();

  const pinchGesture = Gesture.Pinch()
    .onUpdate((event) => {
      scale.value = event.scale;
    })
    .onEnd(() => {
      scale.value = withTiming(1);
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const handleDownload = async () => {
    try {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== 'granted') {
        alert('Permission denied. Cannot save image.');
        return;
      }

      const fileInfo = await FileSystem.getInfoAsync(uri);
      if (!fileInfo.exists) {
        alert('Image file does not exist.');
        return;
      }

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const fileName = `BookScanner_${timestamp}.jpg`;

      const permissions = await FileSystem.StorageAccessFramework.requestDirectoryPermissionsAsync();
      if (!permissions.granted) {
        alert('Permission to access folder denied.');
        return;
      }

      const base64 = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64,
      });

      const newFileUri = await FileSystem.StorageAccessFramework.createFileAsync(
        permissions.directoryUri,
        fileName,
        'image/jpeg'
      );

      await FileSystem.writeAsStringAsync(newFileUri, base64, {
        encoding: FileSystem.EncodingType.Base64,
      });

      Toast.show({
        type: 'success',
        text1: 'Download complete',
        text2: `${fileName} saved to selected folder.`,
        position: 'top',
      });
    } catch (error) {
      console.error('Download error:', error);
      alert('Error saving image.');
    }
  };

  useEffect(() => {
    if (uri) {
      Image.getSize(
        uri,
        (width, height) => {
          const ratio = height / width;
          setImageHeight(SCREEN_WIDTH * ratio);
        },
        (error) => {
          console.error('Failed to get image size', error);
        }
      );
    }
  }, [uri]);

  return (
    <GestureHandlerRootView style={{ flex: 1, width: '100%', alignItems: 'center' }}>
      <View style={styles.container}>
        <TouchableWithoutFeedback
          onPress={() => router.push({ pathname: '/full-image', params: { uri } })}
        >
          <Image
            source={{ uri }}
            style={[
              { width: SCREEN_WIDTH, height: imageHeight },
              animatedStyle,
            ]}
            resizeMode="contain"
          />
        </TouchableWithoutFeedback>

        <View style={[styles.buttonsContainer, { borderColor: border, backgroundColor: background }]}>
          <PrimaryButton title="Download" onPress={handleDownload} />
          <PrimaryButton title="Delete" onPress={onDelete} />
        </View>
      </View>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 20,
  },
  buttonsContainer: {
    flexDirection: 'row',
    padding: 10,
    borderBottomWidth: 1,
    gap: 10,
    width: SCREEN_WIDTH,
    justifyContent: 'flex-end',
  },
});

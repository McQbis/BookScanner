import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Dimensions, Image } from 'react-native';
import { GestureHandlerRootView, GestureDetector, Gesture } from 'react-native-gesture-handler';
import Animated, { useSharedValue, useAnimatedStyle, withTiming } from 'react-native-reanimated';
import * as MediaLibrary from 'expo-media-library';
import * as FileSystem from 'expo-file-system';
import useThemeColors from '@/hooks/useThemeColors';
import PrimaryButton from '@/components/PrimaryButton';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

type ZoomableImageProps = {
  uri: string;
  onDelete: () => void;
};

export default function ZoomableImage({ uri, onDelete }: ZoomableImageProps) {
  const scale = useSharedValue(1);
  const { background, border } = useThemeColors();
  const [imageHeight, setImageHeight] = useState<number>(SCREEN_WIDTH); // default square

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
        alert('Permission to access media library is needed.');
        return;
      }

      const fileUri = FileSystem.documentDirectory + 'book_scanner_downloaded.jpg';
      await FileSystem.copyAsync({ from: uri, to: fileUri });

      const asset = await MediaLibrary.createAssetAsync(fileUri);
      await MediaLibrary.createAlbumAsync('Download', asset, false);

      alert('Photo downloaded to gallery!');
    } catch (error) {
      console.error(error);
      alert('Error downloading photo.');
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
        <GestureDetector gesture={pinchGesture}>
          <Animated.Image
            source={{ uri }}
            style={[
              { width: SCREEN_WIDTH, height: imageHeight },
              animatedStyle,
            ]}
            resizeMode="contain"
          />
        </GestureDetector>

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

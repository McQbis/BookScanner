import { useLocalSearchParams, useRouter } from 'expo-router';
import {
  StyleSheet,
  Pressable,
  Image,
  useWindowDimensions,
} from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withDecay,
  clamp,
} from 'react-native-reanimated';
import {
  Gesture,
  GestureDetector,
  GestureHandlerRootView,
} from 'react-native-gesture-handler';
import React, { useEffect, useState } from 'react';

export default function FullscreenImageViewer() {
  const { uri } = useLocalSearchParams();
  const router = useRouter();
  const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = useWindowDimensions();

  const [imageDimensions, setImageDimensions] = useState({ width: SCREEN_WIDTH, height: SCREEN_HEIGHT });

  useEffect(() => {
    if (uri) {
      Image.getSize(uri as string, (width, height) => {
        const ratio = width / height;
        let finalWidth = SCREEN_WIDTH;
        let finalHeight = finalWidth / ratio;

        if (finalHeight > SCREEN_HEIGHT) {
          finalHeight = SCREEN_HEIGHT;
          finalWidth = finalHeight * ratio;
        }

        setImageDimensions({ width: finalWidth, height: finalHeight });
      });
    }
  }, [uri]);

  const scale = useSharedValue(1);
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);
  const offsetX = useSharedValue(0);
  const offsetY = useSharedValue(0);

  const pinchGesture = Gesture.Pinch()
    .onUpdate((e) => {
      scale.value = e.scale;
    })
    .onEnd(() => {
      if (scale.value < 1) {
        scale.value = withTiming(1);
        translateX.value = withTiming(0);
        translateY.value = withTiming(0);
      }
    });

  const panGesture = Gesture.Pan()
  .onStart(() => {
    offsetX.value = translateX.value;
    offsetY.value = translateY.value;
  })
  .onUpdate((e) => {
    if (scale.value > 1) {
      const scaledWidth = imageDimensions.width * scale.value;
      const scaledHeight = imageDimensions.height * scale.value;

      const boundX = Math.max(0, (scaledWidth - SCREEN_WIDTH) / 2);
      const boundY = Math.max(0, (scaledHeight - SCREEN_HEIGHT) / 2);

      translateX.value = clamp(
        offsetX.value + e.translationX,
        -boundX,
        boundX
      );
      translateY.value = clamp(
        offsetY.value + e.translationY,
        -boundY,
        boundY
      );
    }
  });

  const composed = Gesture.Simultaneous(panGesture, pinchGesture);

  const animatedStyle = useAnimatedStyle(() => {
    const scaledWidth = imageDimensions.width * scale.value;
    const scaledHeight = imageDimensions.height * scale.value;

    return {
      width: scaledWidth,
      height: scaledHeight,
      transform: [
        { translateX: scale.value > 1 ? translateX.value : 0 },
        { translateY: scale.value > 1 ? translateY.value : 0 },
      ],
    };
  });

  return (
    <GestureHandlerRootView style={styles.container}>
      <Pressable style={StyleSheet.absoluteFill} onPress={() => router.back()} />
      <GestureDetector gesture={composed}>
        <Animated.Image
          source={{ uri: uri as string }}
          style={[styles.image, animatedStyle]}
          resizeMode="contain"
        />
      </GestureDetector>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
    justifyContent: 'center',
    alignItems: 'center',
  },
  image: {
    position: 'absolute',
  },
});
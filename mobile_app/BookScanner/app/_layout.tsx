import ThemeToggle from '@/components/ThemeToggle';
import { ThemeProvider } from '@/hooks/ThemeContext';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import { useColorScheme } from 'react-native';
import { AuthProvider } from '@/hooks/useAuth';
import Toast from 'react-native-toast-message';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import * as ScreenOrientation from 'expo-screen-orientation';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const colorScheme = useColorScheme();
  const [loaded] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
  });

  useEffect(() => {
    ScreenOrientation.unlockAsync();

    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) return null;

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <AuthProvider>
        <ThemeProvider>
          <Stack>
            <Stack.Screen name="index" options={{ headerShown: false }} />
            <Stack.Screen name="register" options={{ headerShown: false }} />
            <Stack.Screen name="photo-catalog" options={{ headerShown: false }} />
            <Stack.Screen name="full-image" options={{ headerShown: false }} />
            <Stack.Screen name="+not-found" options={{ title: 'Not Found' }} />
          </Stack>
          <ThemeToggle />
          <StatusBar style="auto" />
          <Toast />
        </ThemeProvider>
      </AuthProvider>
    </GestureHandlerRootView>
  );
}
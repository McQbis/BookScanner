import { useState } from 'react';
import {
  View,
  Image,
  StyleSheet,
  Alert,
  Text,
  TouchableOpacity,
  LayoutAnimation,
  Platform,
  UIManager,
  ScrollView,
} from 'react-native';
import PrimaryButton from '@/components/PrimaryButton';
import * as ImagePicker from 'expo-image-picker';
import useThemeColors from '@/hooks/useThemeColors';
import ConfirmDialog from '@/components/ConfirmDialog';
import { useAuth } from '@/hooks/useAuth';

if (Platform.OS === 'android') {
  UIManager.setLayoutAnimationEnabledExperimental?.(true);
}

export default function PhotoScreen() {
  const { user, logout } = useAuth();
  const [showDialog, setShowDialog] = useState(false);
  const [logoutDialog, setLogoutDialog] = useState(false);
  const { background, text, primary, card, border } = useThemeColors();
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [panelVisible, setPanelVisible] = useState(true);

  const togglePanel = () => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setPanelVisible((prev) => !prev);
  };

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
    <ScrollView contentContainerStyle={[styles.container, { backgroundColor: background }]}>
      {panelVisible ? (
        <View style={[styles.panel, { backgroundColor: background, borderColor: border }]}>
          <PrimaryButton title="Take a photo" onPress={handlePickPhoto} />
          <PrimaryButton title="Choose photo from gallery" onPress={() => Alert.alert('Option 2')} />
          <PrimaryButton title="Logout" onPress={() => {setShowDialog(true); setLogoutDialog(true);}} />
          <PrimaryButton title="Delete account" onPress={() => {setShowDialog(true); setLogoutDialog(false);}} />
          <TouchableOpacity onPress={togglePanel} style={styles.toggle}>
            <Text style={{ color: primary, fontWeight: '600', alignSelf: 'center' }}>
              Hide Options
            </Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={[styles.panel, { backgroundColor: background, borderColor: border }]}>
          <TouchableOpacity onPress={togglePanel} style={styles.toggle}>
            <Text style={{ color: primary, fontWeight: '600', alignSelf: 'center' }}>
                Show Options
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {logoutDialog ? (
        <ConfirmDialog
          visible={showDialog}
          message="Are you sure you want to logout?"
          onCancel={() => setShowDialog(false)}
          onConfirm={() => {
            setShowDialog(false);
            logout()
          }}
        />
      ) : (
        <ConfirmDialog
        visible={showDialog}
        message="Are you sure you want to delete account?"
        onCancel={() => setShowDialog(false)}
        onConfirm={() => {
          setShowDialog(false);
          logout()
        }}
      />
      )}

      {photoUri ? (
        <Image source={{ uri: photoUri }} style={styles.image} />
      ) : (
        <Text style={[styles.placeholder, { color: text }]}>No photo taken yet</Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    paddingTop: 40,
    alignItems: 'center',
  },
  image: {
    width: 200,
    height: 200,
    marginVertical: 20,
    borderRadius: 12,
  },
  placeholder: {
    marginVertical: 20,
    fontSize: 16,
  },
  toggle: {
    marginBottom: 0,
  },
  panel: {
    width: '100%',
    marginBottom: 12,
    padding: 16,
    borderBottomWidth: 1,
    gap: 12,
  },
});

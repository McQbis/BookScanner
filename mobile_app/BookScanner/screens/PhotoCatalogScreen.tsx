import { useState, useCallback } from 'react';
import {
  View,
  Alert,
  Text,
  ScrollView,
  StyleSheet,
  Platform,
  UIManager,
  LayoutAnimation,
  TouchableOpacity,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import PrimaryButton from '@/components/PrimaryButton';
import ConfirmDialog from '@/components/ConfirmDialog';
import ZoomableImage from '@/components/ZoomableImage';
import { useAuth } from '@/hooks/useAuth';
import useThemeColors from '@/hooks/useThemeColors';
import api from '@/lib/api';

if (Platform.OS === 'android') {
  UIManager.setLayoutAnimationEnabledExperimental?.(true);
}

export default function PhotoCatalogScreen() {
  const { token, logout } = useAuth();
  const { background, text, primary, border } = useThemeColors();
  const [photoUris, setPhotoUris] = useState<string[]>([]);
  const [panelVisible, setPanelVisible] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [logoutDialog, setLogoutDialog] = useState(false);

  const togglePanel = useCallback(() => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setPanelVisible((prev) => !prev);
  }, []);

  const handlePickPhoto = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Camera access is needed to take photos.');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        quality: 0.5,
      });

      if (!result.canceled && result.assets?.length > 0) {
        setPhotoUris((prev) => [...prev, result.assets[0].uri]);
      }
    } catch (error) {
      console.error('Error picking photo:', error);
      Alert.alert('Error', 'An error occurred while picking the photo.');
    }
  };

  const handlePickFromGallery = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Gallery access is needed to pick photos.');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsMultipleSelection: false, // or true if you want multi-pick
        quality: 0.5,
      });

      if (!result.canceled && result.assets?.length > 0) {
        setPhotoUris((prev) => [...prev, result.assets[0].uri]);
      }
    } catch (error) {
      console.error('Error picking from gallery:', error);
      Alert.alert('Error', 'An error occurred while picking the photo from gallery.');
    }
  };

  const handleAccountDelete = async () => {
    try {
      const response = await api.delete('/delete-account/', {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.status === 204) {
        setShowDialog(false);
        logout();
        Alert.alert('Success', 'Your account has been deleted.');
      }
    } catch (error: any) {
      console.error(error.response || error.request || error.message);
      Alert.alert(
        'Error',
        error.response
          ? 'Server error occurred while deleting your account.'
          : error.request
          ? 'Network Error. Please check your connection.'
          : 'An unknown error occurred.'
      );
      setShowDialog(false);
    }
  };

  const handleDeletePhoto = useCallback((uriToDelete: string) => {
    setPhotoUris((prev) => prev.filter((uri) => uri !== uriToDelete));
  }, []);

  const renderPanelButtons = () => (
    <>
      <PrimaryButton title="Take a photo" onPress={handlePickPhoto} />
      <PrimaryButton title="Choose photo from gallery" onPress={handlePickFromGallery} />
      <PrimaryButton title="Logout" onPress={() => { setShowDialog(true); setLogoutDialog(true); }} />
      <PrimaryButton title="Delete account" onPress={() => { setShowDialog(true); setLogoutDialog(false); }} />
    </>
  );

  return (
    <ScrollView
      style={{ backgroundColor: background }}
      contentContainerStyle={[
        styles.container,
        { backgroundColor: background },
      ]}
    >
      <View style={[styles.panel, { backgroundColor: background, borderColor: border }]}>
        {panelVisible && renderPanelButtons()}
        <TouchableOpacity onPress={togglePanel} style={styles.toggle}>
          <Text style={{ color: primary, fontWeight: '600', alignSelf: 'center' }}>
            {panelVisible ? 'Hide Options' : 'Show Options'}
          </Text>
        </TouchableOpacity>
      </View>

      <ConfirmDialog
        visible={showDialog}
        message={logoutDialog ? "Are you sure you want to logout?" : "Are you sure you want to delete account?"}
        onCancel={() => setShowDialog(false)}
        onConfirm={logoutDialog ? logout : handleAccountDelete}
      />

      {photoUris.length > 0 ? (
        photoUris.map((uri, index) => (
          <ZoomableImage
            key={index}
            uri={uri}
            onDelete={() => handleDeletePhoto(uri)}
          />
        ))
      ) : (
        <Text style={[styles.placeholder, { color: text }]}>No photos taken yet</Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    paddingTop: 40,
    alignItems: 'center',
    paddingBottom: 100,
  },
  panel: {
    width: '100%',
    marginBottom: 12,
    padding: 16,
    borderBottomWidth: 1,
    gap: 12,
  },
  toggle: {
    marginBottom: 0,
  },
  placeholder: {
    marginVertical: 20,
    fontSize: 16,
  },
});
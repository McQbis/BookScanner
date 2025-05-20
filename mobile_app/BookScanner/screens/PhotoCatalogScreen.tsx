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
import Toast from 'react-native-toast-message';
import { useEffect } from 'react';

if (Platform.OS === 'android') {
  UIManager.setLayoutAnimationEnabledExperimental?.(true);
}

type PhotoEntry = {
  uri: string;
  id: number;
};

export default function PhotoCatalogScreen() {
  const { token, logout } = useAuth();
  const { background, text, primary, border } = useThemeColors();
  const [panelVisible, setPanelVisible] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [logoutDialog, setLogoutDialog] = useState(false);
  const [photos, setPhotos] = useState<PhotoEntry[]>([]);

  const togglePanel = useCallback(() => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setPanelVisible((prev) => !prev);
  }, []);

  const handleUploadPhoto = async (uri:string) => {

    const filename = uri.split('/').pop();
    const match = /\.(\w+)$/.exec(filename ?? '');
    const type = match ? `image/${match[1]}` : `image`;

    const formData = new FormData();
    formData.append('photo', {
      uri,
      name: filename,
      type,
    } as any);

    try {
      const response = await api.post('/photos/upload-photo/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`,
        },
      });

      Toast.show({
        type: 'success',
        text1: 'Upload successful',
        text2: 'Processed photo received.',
      });
      
      const processedUri = response.data.processed_url;
      setPhotos((prev) => [...prev, { uri: processedUri, id: response.data.photo_id }]);
    } catch (error: any) {
      console.error(error.response || error.message);
      Alert.alert('Upload failed', 'An error occurred while uploading.');
    }
  };

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
        await handleUploadPhoto(result.assets[0].uri);
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
        mediaTypes: ['images'],
        allowsMultipleSelection: true,
        quality: 1,
      });

      if (!result.canceled && result.assets?.length > 0) {
        await handleUploadPhoto(result.assets[0].uri);
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

  const handleDeletePhoto = useCallback(
    async (photo: PhotoEntry) => {
      try {
        const response = await api.delete(`/photos/delete-photo/${photo.id}/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 204) {
          setPhotos((prev) => prev.filter((p) => p.id !== photo.id));
          Toast.show({
            type: 'success',
            text1: 'Photo deleted successfully',
          });
        } else {
          Alert.alert('Delete failed', 'Server did not confirm deletion.');
        }
      } catch (error: any) {
        console.error(error.response || error.message);
        Alert.alert('Delete error', 'An error occurred while deleting.');
      }
    },
    [token]
  );

  const fetchUserPhotos = useCallback(async () => {
    try {
      const response = await api.get('/photos/user-photos/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const fetchedPhotos = response.data.map((item: any) => ({
        id: item.photo_id,
        uri: item.processed_url,
      }));

      setPhotos(fetchedPhotos);
    } catch (error: any) {
      console.error('Error fetching photos:', error.response || error.message);
      Alert.alert('Failed', 'Could not fetch your photos.');
    }
  }, [token]);

  useEffect(() => {
    fetchUserPhotos();
  }, [fetchUserPhotos]);

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

      {photos.length > 0 ? (
        photos.map((photo) => (
          <ZoomableImage
            key={photo.id}
            uri={photo.uri}
            onDelete={() => handleDeletePhoto(photo)}
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
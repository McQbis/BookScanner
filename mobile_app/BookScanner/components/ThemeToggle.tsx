import React from 'react';
import { TouchableOpacity, StyleSheet, View } from 'react-native';
import { useTheme } from '@/hooks/ThemeContext';
import { Ionicons } from '@expo/vector-icons';

const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <View style={styles.wrapper} pointerEvents="box-none" >
      <TouchableOpacity
        style={[
          styles.button,
          {
            backgroundColor: theme === 'dark' ? '#333' : '#EEE',
          },
        ]}
        onPress={toggleTheme}
      >
        <Ionicons
          name={theme === 'dark' ? 'sunny' : 'moon'}
          size={24}
          color={theme === 'dark' ? '#FFD60A' : '#1C1C1E'}
        />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: {
    position: 'absolute',
    bottom: 30,
    right: 20,
    zIndex: 999,
  },
  button: {
    backgroundColor: '#FFF',
    borderRadius: 20,
    padding: 20,
    elevation: 5,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
  },
});

export default ThemeToggle;

import useThemeColors from '@/hooks/useThemeColors';
import { View, Text, StyleSheet } from 'react-native';

export default function RegisterScreen() {
  const {background, text, primary, card, border, notification} = useThemeColors();

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Register Page (to be implemented)</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  text: { fontSize: 18 },
});
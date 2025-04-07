import { Pressable, Text, StyleSheet } from 'react-native';
import { Colors } from '@/constants/Colors';

type Props = {
  title: string;
  onPress: () => void;
};

const PrimaryButton = ({ title, onPress }: Props) => (
  <Pressable onPress={onPress} style={styles.button} accessibilityRole="button">
    <Text style={styles.label}>{title}</Text>
  </Pressable>
);

const styles = StyleSheet.create({
  button: {
    backgroundColor: Colors.primary,
    padding: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  label: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});

export default PrimaryButton;
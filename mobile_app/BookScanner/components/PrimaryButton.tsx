import { Pressable, Text, StyleSheet } from 'react-native';
import useThemeColors from '@/hooks/useThemeColors';

type Props = {
  title: string;
  onPress: () => void;
};

const {background, text, primary, card, border, notification} = useThemeColors();

const PrimaryButton = ({ title, onPress }: Props) => (
  <Pressable onPress={onPress} style={styles.button} accessibilityRole="button">
    <Text style={styles.label}>{title}</Text>
  </Pressable>
);

const styles = StyleSheet.create({
  button: {
    backgroundColor: primary,
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
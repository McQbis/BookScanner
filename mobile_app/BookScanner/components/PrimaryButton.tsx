import { Pressable, Text, StyleSheet } from 'react-native';
import useThemeColors from '@/hooks/useThemeColors';

type Props = {
  title: string;
  onPress: () => void;
};

const PrimaryButton = ({ title, onPress }: Props) => {
  const { primary, text } = useThemeColors();

  return (
    <Pressable
      onPress={onPress}
      style={[styles.button, { backgroundColor: primary }]}
      accessibilityRole="button"
    >
      <Text style={[styles.label, { color: text }]}>{title}</Text>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  button: {
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
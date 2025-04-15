import { TextInput, StyleSheet, TextInputProps } from 'react-native';
import useThemeColors from '@/hooks/useThemeColors';

const Input = (props: TextInputProps) => {
  const {background, text, primary, card, border, notification} = useThemeColors();

  return (
    <TextInput
      {...props}
      style={[styles.input, props.style, { backgroundColor: background, color: text, borderColor: border }]}
      placeholderTextColor={text}
    />
  );
};

const styles = StyleSheet.create({
  input: {
    height: 48,
    borderWidth: 1,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 12,
    fontSize: 16,
  },
});

export default Input;
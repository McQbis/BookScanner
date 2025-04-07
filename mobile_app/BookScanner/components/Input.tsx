import { TextInput, StyleSheet, TextInputProps } from 'react-native';
import { Colors } from '@/constants/Colors';

const Input = (props: TextInputProps) => {
  return (
    <TextInput
      {...props}
      style={[styles.input, props.style]}
      placeholderTextColor={Colors.gray}
    />
  );
};

const styles = StyleSheet.create({
  input: {
    height: 48,
    borderColor: Colors.gray,
    borderWidth: 1,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 12,
    fontSize: 16,
  },
});

export default Input;
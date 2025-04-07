import { useColorScheme } from 'react-native';
import { Colors } from '@/constants/Colors';

export const useThemeColors = () => {
  const colorScheme = useColorScheme();
  return {
    background: colorScheme === 'dark' ? Colors.backgroundDark : Colors.backgroundLight,
    text: colorScheme === 'dark' ? Colors.textDark : Colors.textLight,
    gray: Colors.gray,
  };
};

import { useColorScheme } from 'react-native';
import Colors from '@/constants/Colors';

const useThemeColors = () => {
  const colorScheme = useColorScheme();

  const theme = colorScheme === 'dark' ? Colors.dark : Colors.light;

  return {
    ...theme,
    isDark: colorScheme === 'dark',
  };
};

export default useThemeColors;
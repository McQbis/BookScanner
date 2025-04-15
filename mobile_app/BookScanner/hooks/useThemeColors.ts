import Colors from '@/constants/Colors';
import { useTheme } from '@/hooks/ThemeContext';

const useThemeColors = () => {
  try {
    const { theme } = useTheme();

    const selected = theme === 'dark' ? Colors.dark : Colors.light;

    return {
      ...selected,
      isDark: theme === 'dark',
    };
  } catch (error) {
    console.error('useThemeColors must be used within a ThemeProvider:', error);
    return {
      ...Colors.light,
      isDark: false,
    };
  }
};

export default useThemeColors;
import { View, Text, StyleSheet, KeyboardAvoidingView, Platform, TouchableOpacity } from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'expo-router';
import Input from '@/components/Input';
import PrimaryButton from '@/components/PrimaryButton';
import useThemeColors from '@/hooks/useThemeColors';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';
import Toast from 'react-native-toast-message';

const schema = z.object({
  email: z
    .string()
    .email('Invalid email address')
    .min(1, 'Email is required'),  // Email is required and should be valid
  password: z
    .string()
    .min(6, 'Password must be at least 6 characters')
    .regex(/[a-zA-Z0-9]/, 'Password must contain letters and numbers'),  // Ensuring password complexity
  confirmPassword: z
    .string()
    .min(6, 'Please confirm your password')
}).superRefine((data, ctx) => {
  if (data.password !== data.confirmPassword) {
    ctx.addIssue({
      path: ['confirmPassword'],
      message: 'Passwords do not match',
      code: z.ZodIssueCode.custom,
    });
  }
});

type FormData = z.infer<typeof schema>;

export default function RegisterScreen() {
  const { background, primary } = useThemeColors();
  const { login } = useAuth();
  const router = useRouter();
  const { control, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      // Register user
      await api.post('register/', {
        email: data.email,
        password: data.password,
        password2: data.confirmPassword,
      });
  
      // Auto-login after successful registration
      const response = await api.post('token/', {
        username: data.email,
        password: data.password,
      });
  
      const { access } = response.data;
      await login(access, { email: data.email });
  
      // Redirect user to photo page after successful login
      router.replace('/photo-catalog');
  
    } catch (err: any) {
      console.error('Register error:', err.response?.data);
      if (err.response?.status === 400) {
        Toast.show({
          type: 'error',
          text1: 'Registration failed',
          text2: err.response?.data?.detail || 'Something went wrong',
        });
      } else {
        Toast.show({
          type: 'error',
          text1: 'Network error',
          text2: 'Please check your internet connection',
        });
      }
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={[styles.container, { backgroundColor: background }]}
    >
      <Controller
        control={control}
        name="email"
        render={({ field: { onChange, value } }) => (
          <Input
            placeholder="Email"
            value={value}
            onChangeText={onChange}
            keyboardType="email-address"
            autoCapitalize="none"
          />
        )}
      />
      {errors.email && <Text style={[styles.error, { color: 'red' }]}>{errors.email.message}</Text>}

      <Controller
        control={control}
        name="password"
        render={({ field: { onChange, value } }) => (
          <Input
            placeholder="Password"
            value={value}
            onChangeText={onChange}
            secureTextEntry
          />
        )}
      />
      {errors.password && <Text style={[styles.error, { color: 'red' }]}>{errors.password.message}</Text>}

      <Controller
        control={control}
        name="confirmPassword"
        render={({ field: { onChange, value } }) => (
          <Input
            placeholder="Confirm Password"
            value={value}
            onChangeText={onChange}
            secureTextEntry
          />
        )}
      />
      {errors.confirmPassword && <Text style={[styles.error, { color: 'red' }]}>{errors.confirmPassword.message}</Text>}

      <PrimaryButton title="Register" onPress={handleSubmit(onSubmit)} />

      <TouchableOpacity onPress={() => router.replace('/')}>
        <Text style={[styles.link, { color: primary }]}>Already have an account? Log in</Text>
      </TouchableOpacity>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20 },
  link: { marginTop: 20, textAlign: 'center' },
  error: { marginBottom: 8, fontSize: 14 },
});
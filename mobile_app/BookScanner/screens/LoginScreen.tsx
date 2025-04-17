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
  email: z.string().email('Invalid email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type FormData = z.infer<typeof schema>;

export default function LoginScreen() {
  const {background, text, primary, card, border, notification} = useThemeColors();
  const { login } = useAuth();
  const router = useRouter();
  const { control, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      const response = await api.post('token/', {
        email: data.email,
        password: data.password,
      });

      const { access } = response.data;
      await login(access, { email: data.email });

    } catch (err: any) {
      console.error('Login error:', err);
      Toast.show({
        type: 'error',
        position: 'bottom',
        text1: 'Login Failed',
        text2: 'Incorrect email or password',
      });
    }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={[styles.container, { backgroundColor: background }]}>      
      <Controller
        control={control}
        name="email"
        render={({ field: { onChange, value } }) => (
          <Input placeholder="Email" value={value} onChangeText={onChange} keyboardType="email-address" autoCapitalize="none" />
        )}
      />
      {errors.email && <Text style={[styles.error, { color: 'red' }]}>{errors.email.message}</Text>}

      <Controller
        control={control}
        name="password"
        render={({ field: { onChange, value } }) => (
          <Input placeholder="Password" value={value} onChangeText={onChange} secureTextEntry />
        )}
      />
      {errors.password && <Text style={[styles.error, { color: 'red' }]}>{errors.password.message}</Text>}

      <PrimaryButton title="Login" onPress={handleSubmit(onSubmit)} />

      <TouchableOpacity onPress={() => router.push('/register')}>
        <Text style={[styles.link, { color: primary }]}>Don't have an account? Register</Text>
      </TouchableOpacity>
      {/* For implementation of photo page only*/}
      <TouchableOpacity onPress={() => router.push('/photo')}>
        <Text style={[styles.link, { color: primary }]}>Skip</Text>
      </TouchableOpacity>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20 },
  link: { marginTop: 20, textAlign: 'center' },
  error: { marginBottom: 8, fontSize: 14 },
});

import { View, Text, StyleSheet, KeyboardAvoidingView, Platform, TouchableOpacity } from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'expo-router';
import Input from '@/components/Input';
import PrimaryButton from '@/components/PrimaryButton';
import { useThemeColors } from '@/hooks/useThemeColors';
import { Colors } from '@/constants/Colors';

const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type FormData = z.infer<typeof schema>;

export default function LoginScreen() {
  const { background, text, gray } = useThemeColors();
  const router = useRouter();
  const { control, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    router.push('/photo');
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
        <Text style={[styles.link, { color: Colors.primary }]}>Don't have an account? Register</Text>
      </TouchableOpacity>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20 },
  link: { marginTop: 20, textAlign: 'center' },
  error: { marginBottom: 8, fontSize: 14 },
});

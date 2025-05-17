<template>
  <div class="flex flex-col items-center justify-center px-6 pt-8 mx-auto md:h-screen pt:mt-0 dark:bg-gray-900">
    <a href="/" class="flex items-center justify-center mb-8 text-2xl font-semibold lg:mb-10 dark:text-white">
      <span>Flowbite</span>  
    </a>
    <!-- Card -->
    <div class="w-full max-w-xl p-6 space-y-8 sm:p-8 bg-white rounded-lg shadow dark:bg-gray-800">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
        Forgot your password?
      </h2>
      <p class="text-sm text-gray-500 dark:text-gray-400">
        We'll send you a link to reset your password. Enter the email address you used when you joined.
      </p>
      <form class="mt-8 space-y-6" @submit.prevent="handleForgotPassword">
        <div>
          <label for="email" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Your email</label>
          <input v-model="email" type="email" name="email" id="email" class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500" placeholder="name@company.com" required />
        </div>
        <button type="submit" class="w-full px-5 py-3 text-base font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 sm:w-auto dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Reset password</button>
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400">
          Remember your password? <router-link to="/login" class="text-blue-600 hover:underline dark:text-blue-500">Login</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ForgotPassword',
  data() {
    return {
      email: ''
    }
  },
  methods: {
    handleForgotPassword() {
      // In a real app, this would make an API call to send a reset password email
      console.log('Reset password requested for:', this.email);
      
      // For demo purposes, we'll just show a success message and redirect
      alert('Password reset link has been sent to your email.');
      this.$router.push('/login');
    }
  }
}
</script> 
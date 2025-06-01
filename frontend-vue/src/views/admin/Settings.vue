<template>
  <div class="dashboard-card">
    <h2 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">Settings</h2>
    
    <div class="border-b border-gray-200 dark:border-gray-700 mb-4">
      <ul class="flex flex-wrap -mb-px text-sm font-medium text-center text-gray-500 dark:text-gray-400">
        <li class="mr-2">
          <a href="#" @click.prevent="activeTab = 'profile'" :class="[
            'inline-flex items-center justify-center p-4 border-b-2 rounded-t-lg group',
            activeTab === 'profile' ? 
              'text-blue-600 border-blue-600 active dark:text-blue-500 dark:border-blue-500' : 
              'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300'
          ]">
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clip-rule="evenodd"></path>
            </svg>
            Profile
          </a>
        </li>
        <li class="mr-2">
          <a href="#" @click.prevent="activeTab = 'account'" :class="[
            'inline-flex items-center justify-center p-4 border-b-2 rounded-t-lg group',
            activeTab === 'account' ? 
              'text-blue-600 border-blue-600 active dark:text-blue-500 dark:border-blue-500' : 
              'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300'
          ]">
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path d="M5 4a1 1 0 00-2 0v7.268a2 2 0 000 3.464V16a1 1 0 102 0v-1.268a2 2 0 000-3.464V4zM11 4a1 1 0 10-2 0v1.268a2 2 0 000 3.464V16a1 1 0 102 0V8.732a2 2 0 000-3.464V4zM16 3a1 1 0 011 1v7.268a2 2 0 010 3.464V16a1 1 0 11-2 0v-1.268a2 2 0 010-3.464V4a1 1 0 011-1z"></path>
            </svg>
            Account
          </a>
        </li>
        <li class="mr-2">
          <a href="#" @click.prevent="activeTab = 'notifications'" :class="[
            'inline-flex items-center justify-center p-4 border-b-2 rounded-t-lg group',
            activeTab === 'notifications' ? 
              'text-blue-600 border-blue-600 active dark:text-blue-500 dark:border-blue-500' : 
              'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300'
          ]">
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"></path>
            </svg>
            Notifications
          </a>
        </li>
      </ul>
    </div>
    
    <div v-if="activeTab === 'profile'" class="space-y-6">
      <div>
        <label for="fullname" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Full Name</label>
        <input type="text" id="fullname" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="John Doe" value="Neil Sims">
      </div>
      <div>
        <label for="email" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Email address</label>
        <input type="email" id="email" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="john.doe@company.com" value="name@flowbite.com">
      </div>
      <div>
        <label for="bio" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Bio</label>
        <textarea id="bio" rows="4" class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Write your bio here...">Product Manager at Flowbite with a focus on user experience and interface design.</textarea>
      </div>
      <button type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Save changes</button>
    </div>
    
    <div v-if="activeTab === 'account'" class="space-y-6">
      <div>
        <label for="current-password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Current Password</label>
        <input type="password" id="current-password" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="••••••••">
      </div>
      <div>
        <label for="new-password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">New Password</label>
        <input type="password" id="new-password" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="••••••••">
      </div>
      <div>
        <label for="confirm-password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Confirm Password</label>
        <input type="password" id="confirm-password" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="••••••••">
      </div>
      <button type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Change password</button>
    </div>
    
    <div v-if="activeTab === 'notifications'" class="space-y-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white">Email Notifications</h3>
      <ul class="space-y-4">
        <li class="flex items-start">
          <div class="flex items-center h-5">
            <input id="marketing" type="checkbox" class="w-4 h-4 bg-gray-50 rounded border border-gray-300 focus:ring-3 focus:ring-blue-300 dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-blue-600 dark:ring-offset-gray-800" checked>
          </div>
          <div class="ml-3 text-sm">
            <label for="marketing" class="font-medium text-gray-900 dark:text-white">Marketing emails</label>
            <p class="text-gray-500 dark:text-gray-400">Receive emails about new products, features, and more.</p>
          </div>
        </li>
        <li class="flex items-start">
          <div class="flex items-center h-5">
            <input id="product-updates" type="checkbox" class="w-4 h-4 bg-gray-50 rounded border border-gray-300 focus:ring-3 focus:ring-blue-300 dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-blue-600 dark:ring-offset-gray-800" checked>
          </div>
          <div class="ml-3 text-sm">
            <label for="product-updates" class="font-medium text-gray-900 dark:text-white">Product updates</label>
            <p class="text-gray-500 dark:text-gray-400">Get notified when we update our products.</p>
          </div>
        </li>
      </ul>
      <button type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Save preferences</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Settings',
  data() {
    return {
      activeTab: 'profile'
    }
  }
}
</script> 
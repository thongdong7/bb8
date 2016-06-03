function fish_prompt --description 'Write out the prompt'

  set -l last_status $status

  set_color $fish_color_cwd
  echo -n (prompt_pwd)
  set_color normal

  __informative_git_prompt

  if not test $last_status -eq 0
    set_color $fish_color_error
  end

  echo -n ' $ '

end

set -gx PATH ~/dev/bin ~/dev3/bin $PATH
set -gx PATH ~/Android/Sdk/platform-tools $PATH
set -gx ANDROID_HOME ~/Android/Sdk

import requests
import pandas
import os
import random
import bs4
import time
import logging

# # apply proxy if necessary
# import socks
# import socket
# socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 8888)
# socket.socket = socks.socksocket

# hyper-parameters
start = time.time()
manufacturer = 'NVIDIA'
architectures = ['Ampere', 'Turing', 'Volta']
sort = 'released'
mobile = 'No'
delay = 5
output_file = './GPU_Info.csv'
details = {'GPU': None, 'GPU Name': None, 'Architecture': None, 'Foundry': None, 'Process Size': None, 'Transistors': None, 'Die Size': None, 'Release Date': None, 'Availability': None, 'Generation': None, 'Production': None, 'Bus Interface': None, 'Base Clock': None, 'Boost Clock': None, 'Memory Clock': None, 'Memory Size': None, 'Memory Type': None, 'Memory Bus': None, 'Bandwidth': None, 'Shading Units': None, 'TMUs': None, 'ROPs': None, 'SM Count': None, 'Tensor Cores': None, 'RT Cores': None, 'L1 Cache': None, 'L2 Cache': None, 'Pixel Rate': None, 'Texture Rate': None, 'FP16 (half) performance': None, 'FP32 (float) performance': None, 'FP64 (double) performance': None, 'Slot Width': None, 'Length': None, 'Width': None, 'TDP': None, 'Suggested PSU': None, 'Outputs': None, 'Power Connectors': None, 'DirectX': None, 'OpenGL': None, 'OpenCL': None, 'Vulkan': None, 'CUDA': None, 'Shader Model': None, 'GPU Variant': None, 'Launch Price': None, 'Board Number': None, 'Current Price': None, 'Reviews': None, 'Height': None, 'GPU Clock': None}
gpu = pandas.DataFrame(columns=details.keys())
user_agents = [
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
	"Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
	"Mozilla/5.0 (Linux; U; Android 4.4.2; en-us; LGMS323 Build/KOT49I.MS32310c) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 Mobile Safari/537.36",
	"Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 550) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Mobile Safari/537.36 Edge/14.14263"
]
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - [%(levelname)s] %(message)s', datefmt='%m/%d/%Y %H:%M:%S'
)

for architecture in architectures:
	# get basic GPU information
	base = 'https://www.techpowerup.com'
	url = '{}/gpu-specs/?mfgr={}&mobile={}&architecture={}&sort={}'.format(base, manufacturer, mobile, architecture, sort)
	headers = {'User-Agent': random.choice(user_agents)}
	try:
		logging.info('Collecting a list of {} GPU.'.format(architecture))
		response = requests.request('GET', url, headers=headers)
		if response.status_code == 200:
			logging.info('Successfully received the {} GPU data.'.format(architecture))
			response = bs4.BeautifulSoup(response.text, 'lxml')
			div = response.find('div', id='list')
			table = div.find('table')
			df = pandas.read_html(str(table))[0]
			df.columns = df.columns.droplevel(0)
			df['Link'] = [base + tag.find('a').get('href') for tag in table.find_all('td',  'vendor-{}'.format(manufacturer))]
			logging.info('Take a nap.')
			time.sleep(random.randint(delay-1, delay+2))

			# retrieve details for each GPU
			for index, link in enumerate(df['Link']):
				logging.info('Collecting details of {}.'.format(df['Product Name'][index]))
				data = details.copy()
				headers = {'User-Agent': random.choice(user_agents)}
				try:
					sub_response = requests.request('GET', link, headers=headers)
					if sub_response.status_code == 200:
						logging.info('Successfully got the details of {}.'.format(df['Product Name'][index]))
						sub_response = bs4.BeautifulSoup(sub_response.text, 'lxml')
						data['GPU'] = sub_response.find('h1', class_='gpudb-name').text
						sections = sub_response.find_all('section', class_='details')
						for section in sections:
							dd = section.find_all('dd')
							dt = section.find_all('dt')
							for i, _ in enumerate(dt):
								if dt[i].text in data.keys():
									data[dt[i].text] = dd[i].text.replace('\n', '').replace('\t', '')
						gpu = gpu.append(data, ignore_index=True)
					else:
						logging.warning('Got {} responses from the server.'.format(response.status_code))
				except requests.exceptions.RequestException as error:
					logging.exception('{}'.format(error))
				logging.info('Take a nap.')
				time.sleep(random.randint(delay-1, delay+2))
		else:
			logging.warning('Got {} responses from the server.'.format(response.status_code))
	except requests.exceptions.RequestException as error:
		logging.exception('{}'.format(error))
gpu = gpu.rename(columns={'GPU Name': 'GPU Chip'})
logging.info('Finish collecting data.')

# write the collected data into a file
logging.info('Saving the collected data.')
if os.path.isfile(output_file):
	gpu.to_csv(output_file, mode='a', index=False, header=False)
else:
	gpu.to_csv(output_file, mode='w', index=False, header=True)
logging.info('All done!')

print('\n\n------\nTime elapsed: {:.1f}s\n'.format(time.time() - start))
